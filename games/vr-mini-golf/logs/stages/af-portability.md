# Stage af portability research — report only

The cheapest next step is to copy the saved `.rbxl` to the PC and open it locally while signed in as **MetavrseBuilder**, using the existing asset IDs. Expected additional upload/storage cost: **0 Robux**; no place publication is needed. This is a recommendation, not a completed PC test. No file was transferred, no account was changed, and no permission grant or extra upload was performed for this research.

## Concrete findings

- The importer was visibly set to **Upload to Roblox unchecked**. Despite that setting, **all 51 newly imported render meshes** have public metadata identifying owner MetavrseBuilder (`1818120139`) and creation timestamps during this import. `playtests/stage-af/asset-metadata.json` contains every ID, creator, and timestamp. Example: `rbxassetid://101180050716156`, `h07_rope_bridges__PepRed`, type 4 / Mesh, created `2026-10-13T05:31:17.267Z` (Oct 12 PDT).
- Therefore the requested import workflow did create cloud child mesh assets automatically. No explicit upload endpoint, inventory-model upload, Save to Roblox, or Publish was invoked. A strict promise that **no cloud assets were created** would be false. The unchecked option is not an offline-import guarantee.
- Live MeshPart inspection reports `MeshContent.SourceType = Uri`, with `MeshContent` wrapping the same `rbxassetid://...` as `MeshId`; it does not reference an embedded EditableMesh. These props use manifest colors/materials and empty TextureID values.
- The binary input `.rbxl` stores MeshPart `MeshId` strings (2,739 mesh instances, including library copies), plus physical/configuration data. Final batch34 inspection is recorded separately. Render geometry for these URI-backed props depends on asset delivery; the file is not a standalone bundle of their FBX/render vertices. Shared physical/collision strings do not establish embedded render-mesh portability.
- Anonymous asset metadata lookup succeeds. An anonymous asset-delivery request returned HTTP 401, so public metadata does **not** prove that MetavrsePlumber or an unsigned client can fetch the geometry. PC rendering under either account has not been tested.

Roblox's importer documentation describes the upload checkbox as controlling creation of the **model** in Toolbox/Asset Manager. Its unchecked behavior is consistent with the observed absence of an explicitly uploaded inventory model, but does not promise that child mesh creation is suppressed. [Importer settings](https://create.roblox.com/docs/studio/importer)

## Options and cost

| Option | Expected cost | Assessment / authorization needed |
|---|---:|---|
| Copy `.rbxl`, open on PC as its mesh owner | 0 Robux | Cheapest first test. Uses existing cloud mesh references. Requires network access and an authorized owner session; not verified on PC. No new asset upload or place publish. |
| Keep PC on MetavrsePlumber and share existing assets | 0 Robux expected | If assets are restricted, Builder must explicitly grant Plumber access; check ownership/access for older course assets too. This changes permissions and needs Chase's authorization. |
| Save `.rbxlx` | 0 Robux | XML changes serialization, not the URI-backed mesh dependency. Useful for inspection; not an offline embedding solution. Not performed. |
| Package `.rbxm` / `.rbxmx` | 0 Robux | Container preserves mesh references; no reason to expect cloud geometry to become embedded. Not performed. |
| Upload/reimport to Builder inventory through Asset Manager / Importer | Ordinary development models/meshes are free; no Marketplace sale fee is needed | Redundant for the 51 confirmed existing child meshes. Creates model/asset inventory entries and may duplicate IDs. Needs explicit upload authorization; not performed. |
| Open Cloud Assets API | No paid service is necessary for this task | Requires an authorized asset-write API key/OAuth scope and creator context. FBX uploads use the Model path, with a 20 MB per-request limit; raw Mesh upload accepts Roblox mesh data, not arbitrary FBX. No key was created/read and no API upload was performed. |

Roblox distinguishes compact `.rbxl` from XML `.rbxlx`; assets normally remain cloud references. [Place formats](https://create.roblox.com/docs/projects/place-files), [asset storage](https://create.roblox.com/docs/projects/assets)

For restricted assets, grant access to the intended collaborator rather than assuming a copied place grants rights. Individual collaborator grants require a Roblox friendship. Open Use is irreversible, and game grants cannot be revoked. Moderation and asset permissions can affect rendering; changing the file extension does not bypass them. [Asset privacy and sharing](https://create.roblox.com/docs/projects/assets/privacy)

Development creation/sharing is free; avatar Marketplace listing fees are a separate workflow. [Roblox creation costs](https://create.roblox.com/docs/art/accessories/creating) Open Cloud supports asset uploads independently of place publication, but adds credentials and upload steps that are unnecessary for these already-created mesh IDs. [Assets API](https://create.roblox.com/docs/cloud/guides/usage-assets)

## Final saved-file verification
The final batch34 file is 3447258 bytes; SHA256 `3bde4e643dae002a2422ee929887a400a6126810b16590622eaab8d57e7292ff`. All 51 newly imported MeshIds are present among 2837 serialized MeshId entries. The MeshPart class has no MeshData property; a separate class has 37 MeshData strings, all empty. Live MeshContent values were URI-backed. Physics/shared-string payloads do not establish embedded render geometry. Copying this file therefore preserves asset references, not a self-contained render-mesh package. Full decoded property evidence is in `playtests/stage-af/batch34-file-inspection.json`.
