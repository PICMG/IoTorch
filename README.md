# IoTorch Microcontroller Communications Libraries for Industrial Internet of Things

![License](https://img.shields.io/github/license/PICMG/IoTorch)
![Coverage](https://img.shields.io/codecov/c/github/PICMG/IoTorch)
![Issues](https://img.shields.io/github/issues/PICMG/IoTorch)
![Forks](https://img.shields.io/github/forks/PICMG/IoTorch)
![Stars](https://img.shields.io/github/stars/PICMG/IoTorch)
![Last Commit](https://img.shields.io/github/last-commit/PICMG/IoTorch)


IoTorch is a series of libraries for embedded microcontroller platforms that implement robust industrial communications protocols over serial interfaces using the Management Component Transport Protocol (MCTP), and Platform Level Data Model (PLDM) both from the Distributed Management Task Force (DMTF).  Copies of these specifications may be freely downloaded from the DMTF here:
- [MCTP Specification](https://www.dmtf.org/documents/pmci/management-component-transport-protocol-mctp-base-specification-131)
- [PLDM Specification](https://www.dmtf.org/sites/default/files/standards/documents/DSP0240_1.2.0.pdf)

Together, these two specifications provide lightweight, robust transport and application-layer data communications suitable for small-scale embedded devices.

The first goals of this project, by phase are:
- **Phase 1** 
    - Implement Linux-based test environment for valiation of MCTP, leveraging existing Linux support.
    - Implement MCTP communications support for Arduino devices with testing on Uno, and NanoEvery platforms.
    - Develop release process for MCTP library code
- **Phase 2**
    - Implement PLDM server code for Uno and NanoEvery that communicates on top of MCTP protocol
    - Implement Linux client and validation strategy for PLDM endpoints.
    -- Develop release process for PLDM library code
- **Phase 3**
    -- Implement MCTP and PLDM for additional tbd processor architecture

---

## Other Resources

The PICMG organization has already written MCTP code for two microcontroller architectures which may be a useful reference for this project.
- [PICMG IoT Firmware Refererence Code](https://github.com/PICMG/iot_firmware)
