# NP-toys

My network programming toy projects.

Now projects are mostly from _Computer Networking: A Top-Down Approach_ 's assignments.

I refactor the code and add features I want based on the assignments provided by the book.

代码稀烂，正在学习中

## Content

### toy Web server

- can handle very simple HTTP request and send response.
- status code: 200, 400, 404 / method: GET are supported.
- very naive. Single-threaded, synchronous.
- been tested on Firefox/Chrome.
- A toy for learning. Might be improved in the future.

### UDP ping program

- a simple ping server/client using UDP sockets
- determine round-trip time for each packet
- calculate packet loss rate

### toy e-mail client

- a simple SMTP client that can send plain text.
- in other words, a clumsy implementation of reduced `smtplib`.
- just plain ascii, not support utf8/html/attach yet. May be improved someday.

### toy Web proxy server

TODO

### ICMP ping program

TODO

### RTP/RTSP server

TODO


