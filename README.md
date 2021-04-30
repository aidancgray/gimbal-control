# Software for running the 'Gimbalator' System for PFS.

```gimbal_server.py``` is the old version.
```gimbal_server_v2.py``` is the new version.
  
## Command Set

| Command           | Args                  | Return                           | Description                                 |
|      :----:       |       :----:          |              :----:              |                                         ---:|
|-- Monochromator --|-----------------------|----------------------------------|---------------------------------------------|
| mono              | ?                     | on/off;wavelength;OK             | Query status                                |
|                   | on/off                | 'OK' when done                   | Turn lamp on/off                            |
|                   | 0-1750                | 'OK' when done                   | Move to wavelength                          |
|                   | home                  | 'OK' when done                   | Home the motor                              |
|----- Stages ----- |-----------------------|----------------------------------|---------------------------------------------|
| home              | x/y                   | 'OK' when done                   | Homes the given axis                        |
| move              | 100-60000 100-29000   | 'OK' when done                   | Move to the 'x y' position                  |
| stages            | ?                     | 'X=STEPS;Y=STEPS;OK              | Query stage positions                       |
|------ LEDs ------ |-----------------------|----------------------------------|---------------------------------------------|
| led               | ?                     | wavelength=#%;...for each LED;OK | Query LED list status                       |
|                   | [wavelength] 0-100    | 'OK' when done                   | Sets the desired LED to the desired power % |
