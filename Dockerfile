
FROM fedora:38

ENV DISPLAY=:0
COPY . .

RUN groupadd --g 1000 user 
RUN useradd --uid 1000 --gid 1000 --home /partage_biere   user

RUN dnf -y upgrade 
RUN dnf -y install python3 python3-pip
RUN python3 -m pip install -r dependencies.txt
RUN dnf install -y mesa-libGLU libxkbcommon libxkbcommon-x11 mesa-libEGL fontconfig dbus-libs xcb-util-cursor xcb-util-wm xcb-util-keysyms xauth abattis-cantarell-fonts
RUN xauth merge /dot.xauthority
USER 1000:1000
#remove /app_dev from the command line once everything is ok
CMD [ "python3", "/app_dev/main.py" ]