---
name: New Modem Support
about: Request support for a new Alcatel modem model
title: '[NEW MODEM] '
labels: enhancement, help wanted
assignees: ''
---

## Modem Information
- **Model name**: (e.g., MW50V)
- **Firmware version**: (if known)
- **Hardware version**: (if known)
- **API endpoint**: (e.g., /jrd/webapi)

## Compatibility Check
- [ ] The modem uses the `/jrd/webapi` endpoint
- [ ] I can access the modem's web interface
- [ ] I have admin credentials

## Test Results
Please run `alcatel doctor` and paste the output:

```json
Paste diagnostic output here (redact sensitive information)
```

## Test Commands
Please test the following commands and report results:

- [ ] `alcatel system status -u http://MODEM_IP` (should work without password)
- [ ] `alcatel system poll-extended -u http://MODEM_IP -p PASSWORD` (requires password)
- [ ] `alcatel sms list -u http://MODEM_IP -p PASSWORD` (if SMS is supported)

## Authentication Method
Describe how authentication works:
- [ ] Uses standard encryption (like MW40V1/HH72)
- [ ] Uses different encryption method
- [ ] Uses unencrypted login
- [ ] Other (please describe)

## Differences from Existing Models
List any differences you noticed compared to existing supported models:
- Authentication method differences
- API response format differences
- Missing or additional endpoints
- Other notable differences

## Network Traffic Capture (Optional but Helpful)
If possible, please capture network traffic using Wireshark or browser developer tools:
- [ ] I can provide captured traffic (anonymized)
- [ ] I need help capturing traffic
- [ ] I cannot capture traffic

## Additional Information
Any other information that might be helpful:
- Links to modem documentation
- Screenshots of the web interface
- Any reverse engineering notes
- Related issues or discussions

