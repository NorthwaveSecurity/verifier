
; <<>> DiG 9.10.6 <<>> @8.8.8.8 google.com +dnssec +multi
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 27449
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags: do; udp: 512
;; QUESTION SECTION:
;google.com.		IN A

;; ANSWER SECTION:
google.com.		138 IN A 142.251.39.110

;; Query time: 51 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Tue Mar 15 09:16:14 CET 2022
;; MSG SIZE  rcvd: 55

