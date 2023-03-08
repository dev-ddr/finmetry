# ddr_mfc

Pakcage uses alicat python package to control the alicat made mass flow controllers. This package is built upon that package. By installing this package, alicat is installed automatically as a requirement.

### Install ddr_mfc
Install ddr_davis_data using pip.
```py
pip install ddr_mfc
```
### Instantiation

```py
import ddr_mfc
print(ddr_davis_data.version)
```

    0.0.2
    

to start the flow controller you will need to know in which port the flow controller is connected. Also the address of the flow controller is required. This can be set from the controller itself. You can go in `menu` in flow controller device and look for `address` in there somewhere. You need different address for different mfc connected with same USB camble to the PC.

```py
mfc1 = ddr_mfc.mfc(port='COM6',address='A',name='mfc_air')
```

By giving the name to the MFC, you can distinguish among the MFC data. The `read` function of the mfc used `name` as a suffix to the variable.

```py
mfc1.read()
```

This will read the data from the MFC.

```py
mfc1.set_SLPM(slpm=30)
```

This will set the SLPM to 30. Sometimes serial communication gives error. These functions uses `try-except` of python to navigate through error of serial comunication.

```ddr_mfc.mfc``` class is inherited from `alicat.FlowController` class. Hence the functionalities and documentation on [ALICAT PACKAGE](https://github.com/numat/alicat) will help guide futher.

---
---
