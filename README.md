# Software for running the 'Gimbalator' System for PFS.

```gimbal_server_v2.py``` is the newest version.

The pigpio daemon starts as a system process upon boot-up.

Connect via port 9999.

## Things to note:
- Two different LEDs cannot be run simultaneously.
- An LED and the Monochromator CAN be run simultaneously. Ensure one is off before using the other (unless desired).
- Motor controllers lose telemetry upon power loss. Although power loss is unlikely, homing can and should be done upon each new measurement run; this includes the monochromator.
- Homing is done at a very slow speed to ensure repeatability.
- Turn off monochromator lamp ```mono off``` when not in use for extended periods of time. (Don't burn out the lamp!) 
  
## Command Set

| Command           | Arg(s)                     | Return                           | Description                                 |
|      :----:       |       :----:               |              :----:              |                                         ---:|
|-- Monochromator --|----------------------------|----------------------------------|---------------------------------------------|
| mono              | ?                          | on/off;wavelength;OK             | Query status                                |
| mono              | on/off                     | 'OK' when done                   | Turn lamp on/off                            |
| mono              | 0-1750                     | 'OK' when done                   | Move to wavelength                          |
| mono              | home                       | 'OK' when done                   | Home the motor                              |
|----- Stages ----- |----------------------------|----------------------------------|---------------------------------------------|
| home              | x/y                        | 'OK' when done                   | Homes the given axis                        |
| move              | 100-60000 100-29000        | 'OK' when done                   | Move to the 'x y' position                  |
| stages            | ?                          | 'X=STEPS;Y=STEPS;OK              | Query stage positions                       |
| microstep         | x/y 2/4/8/16/32/64/128/265 | 'OK' when done                   | Changes the desired stage's microstep mode  |
|------ LEDs ------ |----------------------------|----------------------------------|---------------------------------------------|
| led               | ?                          | wavelength=%%;...for each LED;OK | Query LED list status                       |
| led               | wavelength 0-100           | 'OK' when done                   | Sets the desired LED to the desired power % |
