# Bailey-Cloud-DNS-Proxy-Filter POC
A fancy content filtration system proof of concept, built upon OpenVPN, Pi-Hole DNS, and mitm proxy. Deployed on Google Cloud.
Useful concept for creating a safe environment for children, families, and human beings who would desire to set boundaries for innapropriate and harmful content on the web.
- Family Safety and Internet Web Content Filer
- Usage on the go with cloud availability
- An attempt to keep up with an ongoing arms race on the internet to conquer evil.
Thanks to the open source community.

Folder Description:

- Bailey: VPN kill switch, misc. support scripts and Pi Hole DNS export data
- Granville: mitm proxy scripts for filtering http(s) requests with search key words


NOTE: In order to deploy this solution in the cloud, security adjustments must be made. Environment was set up on a Debian system via Google Cloud based on the guides below.

- Pi Hole + OpenVPN Instructions (Wireguard requires Admin on windows)

https://github.com/rajannpatel/Pi-Hole-PiVPN-on-Google-Compute-Engine-Free-Tier-with-Full-Tunnel-and-Split-Tunnel-OpenVPN-Configs#finalize-vpn-confgurations-on-server

- Combined with some instructions here:

https://docs.pi-hole.net/guides/vpn/firewall/
