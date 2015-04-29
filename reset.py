import ps_drone

drone = ps_drone.Drone()       # Initializes the PS-Drone-API
drone.startup()                # Connects to the drone and starts subprocesses
drone.reset()
