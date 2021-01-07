# ocio_lut_prescription

---

## Summary
ocio_lut_prescription is a gui tool used to wrap the ociobakelut command

---

## UI Overview

Note: If you are already familiar with ociobakelut, the ui should be fairly simple to figure out.

![](.docs/fullUI.png)

## Generate a LUT, step by step
### Load your ocio configuration
![](.docs/setConfig.png)

### Select Input and Output ColorSpace (or looks, if available)
![](.docs/setInOut.png)

### Select Lut Format
![](.docs/setFormat.png)

### Select Destination and bake
![](.docs/setBake.png)

## Extra Features
- Persistent settings for ease of repeated use

- system/dark mode

![](.docs/setDarkStyle.png)

- expand window for operation summary
![](.docs/expandPrescriptionInfo.png)


## Prerequesites
- PyOpenColorIOv2
- python3.8
- pyside2

---

## install
`pip install ocio_lut_prescription`


## Environment setup example (in a linux .bashrc)
```
# OCIO
export PYTHONPATH="${PYTHONPATH}:/path/to/compiled/ocio/lib/python3.8/site-packages"
export LD_LIBRARY_PATH="/path/to/compiled/ocio/lib:$LD_LIBRARY_PATH"
export PATH="/path/to/compiled/ocio/bin:$PATH"
```

---

## execute
`ocio_lut_prescription` (in Terminal)

---

## tests
`tox` (in terminal) will run tests/pylint/black on the repo

## Release history

v1.0.0: initial release

---
## Misc

##### Icon copyright

![](.docs/prescription.png)


---

##### Disclaimer

I'm not a doctor, those ain't real prescriptions.

---
