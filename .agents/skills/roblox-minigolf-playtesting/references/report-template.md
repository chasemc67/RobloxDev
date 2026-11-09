# Playtest report template

```markdown
# <Course/place> playtest: <round name>

## Scope
- Places and versions: <place (role)> v<N> (handoff | seen in Version History), local copy <file name>
- Focus this round: <e.g. newest course deep, others smoke | world only | flow only>
- Devices and modes: <desktop | phone emulator | SimulateVR | live>
- Out of scope: <item> (<who decided>)
- Machine, mode, harness revision, seeds and options: <...>

## Findings
1. **P1** <one line>. Owner: <build | model | layout | machine owner>
   - Repro: hole <n>, spot <x,z hole-local>, aim <deg>, speed <studs/s> or seed <s>, phase <t>, <device/mode>, <steps>
   - Expected / actual: <...> / <...>
   - Frequency: <k/n>. Evidence tier: <engine | probe | manual | simulator>
   - Evidence: <numbers>, <screenshot path (not in git)>
2. ...

## Simulator comparison (only if in scope)
| Hole | Measure and definition | Engine (policy, n) | Simulator (model, policy, n) | Target band (source) |
|---|---|---|---|---|

Authored par stays as written. Measured recommendations, if any: <hole>: <value> (<policy>, n=<n>).

## Passes
- <check>: pass (<n> shots / <n> holes)

## Not tested, and why
- Real headset: SimulateVR only
- Real phone: emulator only
- Live server: <...>
- <other gaps>

## Retest (if this is a rerun)
| Finding | Before (v<N>) | After (v<M>) | Status (fixed / still there / new) |
|---|---|---|---|
Method changes since last run: <none | ...>
```
