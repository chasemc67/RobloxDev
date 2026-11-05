"""Render-only sheet inputs. Never edits or exports approved/fixed assets."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import json
import math
import bpy
import numpy as np
from mathutils import Vector
from common import S, D, CHANGED, records, guard, load_cache, write_json
from clearance import solids, FACES


def B(v):
    return Vector((v[0], -v[2], v[1]))


def material(name, colour):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*colour, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*colour, 1)
    shader.inputs['Roughness'].default_value = .72
    return mat


def render(p, stage, view, boxes, contact, feature):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    path = D / p['source_fbx'] if stage == 'before' else D / f"models/fbx/props_fix_overlap/{p['id']}.fbx"
    bpy.ops.import_scene.fbx(filepath=str(path))
    sc = bpy.context.scene
    assets = [o for o in sc.objects if o.type == 'MESH']
    if not assets:
        raise RuntimeError('Empty asset: ' + str(path))
    palette = {m['material']: m.get('colour', m.get('color')) for m in p['meshes']}
    for obj in assets:
        key = obj.name.split('__')[-1].split('.')[0]
        colour = palette[key].lstrip('#')
        obj.data.materials.clear()
        obj.data.materials.append(material(key, tuple(int(colour[i:i+2], 16)/255 for i in (0, 2, 4))))
        for face in obj.data.polygons:
            face.material_index = 0
    anchor = np.array(p['anchor_local'])
    for box in boxes:
        mesh = bpy.data.meshes.new(box['id'])
        mesh.from_pydata([B(v-anchor) for v in box['vertices']], [], FACES)
        mesh.update()
        obj = bpy.data.objects.new(box['kind']+'_'+box['id'], mesh)
        sc.collection.objects.link(obj)
        mesh.materials.append(material(box['kind'], (.68, .70, .73) if box['kind'] == 'felt' else (.17, .19, .22)))
    # Conservative AABBs include every imported mesh and every context solid.
    bounds = []
    for obj in sc.objects:
        if obj.type == 'MESH':
            pts = np.array([tuple(obj.matrix_world @ Vector(v)) for v in obj.bound_box])
            bounds.append((pts.min(0), pts.max(0)))
    points = np.array([tuple(o.matrix_world @ v.co) for o in assets for v in o.data.vertices])
    lo, hi = points.min(0), points.max(0)
    target = B(np.array(contact['mesh_point'])-anchor) if view == 'close' else Vector((lo+hi)/2)
    camera = bpy.data.objects.new('SheetCamera', bpy.data.cameras.new('SheetCamera'))
    sc.collection.objects.link(camera)
    sc.camera = camera
    camera.data.type = 'ORTHO'
    # Same feature scale for the before/after pair; low side angle on the stone.
    elevation = .16 if view == 'close' and p['id'] == 'h06_respawn_stone' else (.65 if view == 'close' else .8)
    distance = 3*feature if view == 'close' else 3*float(np.linalg.norm(hi-lo))
    candidates = []
    for step in range(24):
        angle = -math.pi/3 + step*math.tau/24
        direction = Vector((math.cos(angle), math.sin(angle), elevation)).normalized()
        location = target + direction*distance
        if any(np.all(np.array(location) >= a-.05) and np.all(np.array(location) <= b+.05) for a, b in bounds):
            continue
        # Prefer an unobstructed approach to the contact; tolerate only the
        # immediate contact surface itself, never a remote rail/felt occluder.
        hit, pos, *_ = sc.ray_cast(bpy.context.evaluated_depsgraph_get(), location, -direction, distance=distance)
        obstruction = (pos-target).length if hit else 0
        candidates.append((obstruction, step, location))
    if not candidates:
        raise RuntimeError('No outside camera at 3x feature size: '+p['id'])
    obstruction, _, location = min(candidates, key=lambda item: item[:2])
    if view == 'close' and obstruction > feature*.45:
        raise RuntimeError('Contact obscured; refusing unreadable close-up: '+p['id'])
    camera.location = location
    camera.rotation_euler = (target-location).to_track_quat('-Z', 'Y').to_euler()
    if view == 'close':
        camera.data.ortho_scale = feature*2.3
    else:
        # Fit projected bbox with 15% padding on each side, including aspect.
        inverse = camera.rotation_euler.to_matrix().transposed()
        projected = np.array([tuple(inverse @ (Vector(v)-target)) for v in points])
        span = np.ptp(projected, axis=0)
        camera.data.ortho_scale = max(span[0], span[1]*900/700)*1.30
    camera.data.clip_start = .01
    camera.data.clip_end = max(1000, distance*10)
    marker = B(np.array(contact['mesh_point'])-anchor)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=min(.10, feature*.035), location=marker)
    bpy.context.object.name = 'WorstContact_Red'
    bpy.context.object.data.materials.append(material('ContactRed', (1, .015, .015)))
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 32
    sc.render.resolution_x, sc.render.resolution_y = 900, 700
    sc.render.resolution_percentage = 100
    sc.world = bpy.data.worlds.new('SheetWorld')
    sc.world.use_nodes = True
    sc.world.node_tree.nodes['Background'].inputs[0].default_value = (.22, .25, .30, 1)
    sc.world.node_tree.nodes['Background'].inputs[1].default_value = .7
    sun = bpy.data.objects.new('SheetSun', bpy.data.lights.new('SheetSun', 'SUN'))
    sc.collection.objects.link(sun)
    sun.data.energy = 2
    sun.rotation_euler = (.4, -.5, -.4)
    sc.view_settings.view_transform = 'Standard'
    folder = S/'renders/sheet08'
    folder.mkdir(parents=True, exist_ok=True)
    sc.render.filepath = str(folder/f"{p['id']}_{stage}_{view}.png")
    bpy.ops.render.render(write_still=True)
    return dict(asset=p['id'], stage=stage, view=view, camera=list(location), target=list(target), distance=distance, feature_size=feature, obstruction=obstruction, outside_all_bounds=True)


def main():
    guard('check')
    holes = {h['number']: h for h in json.loads((D/'holes.json').read_text())['holes']}
    results = {stage: json.loads((S/f'clearance_{stage}.json').read_text()) for stage in ('before', 'after')}
    audit = []
    for p in records('after'):
        if not p['source_fbx'].startswith('models/fbx/props_batch3/'):
            raise RuntimeError('Expected approved batch3 FBX')
        # Verify fitcheck cache provenance without rewriting any fitcheck data.
        caches = {stage: load_cache(p, stage) for stage in ('before', 'after')}
        contacts = {stage: min(results[stage][p['id']].values(), key=lambda r: r['clearance']) for stage in caches}
        sizes = []
        for stage, ts in caches.items():
            tri = ts[contacts[stage]['triangle']]
            sizes.append(max(.8, float(np.linalg.norm(np.ptp(tri, axis=0)))))
        feature = max(sizes)
        boxes = solids(holes[p['hole']])
        for view in ('34', 'close'):
            for stage in ('before', 'after'):
                audit.append(render(p, stage, view, boxes, contacts[stage], feature))
    guard('check')
    write_json(S/'sheet_cameras.json', audit)


if __name__ == '__main__':
    main()
