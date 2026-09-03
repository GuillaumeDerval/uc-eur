#!/usr/bin/env julia
#
# Fill in the initial commitment state of generated instances, in place.
#
#   julia --project=julia julia/add_initial_conditions.jl instances
#   julia --project=julia julia/add_initial_conditions.jl path/to/one.json
#
# The Python generator deliberately writes no initial state: there is no dataset
# of what was running the hour before a chosen week, and asserting one distorts
# the answer (cold-starting a whole national fleet forces load shedding that
# reflects the assumption, not the power system).
#
# This step derives a feasible, self-consistent state with UnitCommitment.jl's
# own `generate_initial_conditions!`, which solves a single-period MIP against
# the first hour's demand, and writes "Initial status (h)" and
# "Initial power (MW)" back into the instance. Instances are then self-contained
# for any solver, not only UnitCommitment.jl.

using UnitCommitment, JuMP, HiGHS, JSON, Printf, GZip

const target = length(ARGS) >= 1 ? ARGS[1] : "instances"
const optimizer = optimizer_with_attributes(HiGHS.Optimizer, "output_flag" => false)

function instance_files(target::String)
    isfile(target) && return [target]
    files = String[]
    for (root, _, names) in walkdir(target), f in names
        if (endswith(f, ".json") || endswith(f, ".json.gz")) &&
           !endswith(f, ".summary.json") && !startswith(f, "results") &&
           f ∉ ("index.json", "congestion.json")
            push!(files, joinpath(root, f))
        end
    end
    return sort(files)
end

"""
Write the derived state into the raw JSON rather than re-serialising the parsed
instance, so every field the generator wrote survives untouched.

`read` multiplies a status in hours by `60 ÷ time step`, so invert that on the
way out to keep the file in the units the format documents.
"""
function add_initial_conditions!(path::String)
    raw = endswith(path, ".gz") ?
        GZip.open(path, "r") do io
            JSON.parse(io; dicttype = Dict, inttype = Int64)
        end :
        JSON.parsefile(path; dicttype = Dict, inttype = Int64)
    generators = raw["Generators"]

    already = count(
        g -> haskey(g, "Initial status (h)") && haskey(g, "Initial power (MW)"),
        values(generators),
    )
    thermal = count(g -> lowercase(get(g, "Type", "")) == "thermal", values(generators))
    already == thermal && return (thermal, 0, "already present")

    instance = UnitCommitment.read(path)
    UnitCommitment.generate_initial_conditions!(instance, optimizer)

    step = get(raw["Parameters"], "Time step (min)", 60)
    multiplier = 60 ÷ step

    updated = 0
    clamped = 0
    for g in instance.scenarios[1].thermal_units
        entry = generators[g.name]
        status = g.initial_status ÷ multiplier
        # A zero status is invalid in the format; the sign carries on/off.
        status == 0 && (status = g.initial_status > 0 ? 1 : -1)

        power = g.initial_power
        if status > 0
            # `generate_initial_conditions!` solves a single-period MIP that
            # knows nothing about ramp or shutdown limits, so it can leave a
            # unit above the level it is allowed to shut down from. The horizon
            # is then infeasible whenever the schedule needs that unit off
            # early: the unit can neither stay on nor legally stop.
            curve = entry["Production cost curve (MW)"]
            pmin, pmax = float(first(curve)), float(last(curve))
            cap = pmax
            if haskey(entry, "Shutdown limit (MW)")
                cap = min(cap, float(entry["Shutdown limit (MW)"]))
            end
            cap = max(cap, pmin)          # never below the minimum stable level
            if power > cap + 1e-6
                power = cap
                clamped += 1
            end
            power = clamp(power, pmin, pmax)
        else
            power = 0.0                   # offline units produce nothing
        end

        entry["Initial status (h)"] = status
        entry["Initial power (MW)"] = round(power, digits = 4)
        updated += 1
    end
    clamped > 0 && @printf("          (clamped %d unit(s) to their shutdown limit)\n", clamped)

    if endswith(path, ".gz")
        GZip.open(path, "w") do io; JSON.print(io, raw, 1); end
    else
        open(path, "w") do io; JSON.print(io, raw, 1); end
    end
    update_summary!(path, updated)
    return (thermal, updated, "generated")
end

"""
Keep the sibling summary truthful: the Python generator records
`initial_conditions: "free"`, which stops being the case once a state is baked
into the instance.
"""
function update_summary!(path::String, updated::Int)
    summary_path = replace(path, r"\.json(\.gz)?$" => ".summary.json")
    isfile(summary_path) || return
    meta = JSON.parsefile(summary_path; dicttype = Dict, inttype = Int64)
    haskey(meta, "options") && (meta["options"]["initial_conditions"] = "generated")
    meta["initial_conditions"] = Dict(
        "source" => "UnitCommitment.jl generate_initial_conditions!",
        "method" => "single-period MIP against the first hour's demand",
        "units_set" => updated,
        "note" => "no observational dataset of pre-horizon commitment exists; " *
                  "this state is derived from the instance itself",
    )
    open(summary_path, "w") do io
        JSON.print(io, meta, 1)
    end
end

files = instance_files(target)
@printf("adding initial conditions to %d instance(s)\n\n", length(files))

failed = 0
for (i, f) in enumerate(files)
    try
        thermal, updated, how = add_initial_conditions!(f)
        @printf("[%3d/%3d] %-34s %3d thermal units, %s\n",
                i, length(files), basename(f), thermal, how)
    catch e
        global failed += 1
        @printf("[%3d/%3d] %-34s FAILED: %s\n",
                i, length(files), basename(f), sprint(showerror, e))
    end
    flush(stdout)
end

@printf("\n%d/%d instances updated\n", length(files) - failed, length(files))
exit(failed == 0 ? 0 : 1)
