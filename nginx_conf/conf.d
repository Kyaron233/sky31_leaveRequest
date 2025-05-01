server {
    listen 80;
    server_name blog.ruarua.site;

    location /client/ {
        root /var/web/client;
        index index.html;
        try_files $uri $uri/ index.html;
    }

    # 管理端页面 http://AAA/administrator
    location /administrator {
        root /var/web/managementEnd;
        index index.html;
        try_files $uri $uri/ index.html;
    }

    # 公共资源
    location /lib/ {
        root /var/web;
    }

    location /ChillReunion/ {
        root /var/web;
    }

    location /PingFang/ {
        root /var/web;
    }


    location /user/ {
        proxy_pass http://127.0.0.1:8000/user/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}