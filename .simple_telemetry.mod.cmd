savedcmd_simple_telemetry.mod := printf '%s\n'   simple_telemetry.o | awk '!x[$$0]++ { print("./"$$0) }' > simple_telemetry.mod
