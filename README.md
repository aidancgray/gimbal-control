# Software for running the 'Gimbalator' System for PFS.

```gimbal_server.py``` is the old version.
```gimbal_server_v2.py``` is the new version.
  
## Command Set

| Command | Args                | Description                                 |
|---------|---------------------|---------------------------------------------|
| mono    | ?                   | Query status                                |
|         | on/off              | Turn lamp on/off                            |
|         | 0-1750              | Move to wavelength                          |
|         | home                | Home the motor                              |
|---------|---------------------|---------------------------------------------|
| home    | x/y                 | Homes the given axis                        |
| move    | 100-60000 100-29000 | Move to the 'x y' position                  |
| stages  | ?                   | Query stage positions                       |
|---------|---------------------|---------------------------------------------|
| led     | ?                   | Query LED list status                       |
|         | [wavelength] 0-100  | sets the desired LED to the desired power % |
