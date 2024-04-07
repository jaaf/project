#!/bin/bash
if [ -d "package" ]; then rm -Rf package; fi
rm -f biere*.rpm
mkdir -p package/opt
mkdir -p package/usr/share/applications
mkdir -p package/usr/share/icons/hicolor/scalable/apps
cp -r dist/linux/main package/opt/biere 
cp base-data/icons/biere-64x64.png package/usr/share/icons/hicolor/scalable/apps/biere-64x64.png
cp biere.desktop package/usr/share/applications
find package/opt/biere -type f -exec chmod 644 -- {} +
find package/opt/biere -type d -exec chmod 755 -- {} +--
find package/usr/share -type f -exec chmod 644 -- {} + 
chmod +x package/opt/biere/biere
fpm -C package -s dir -t deb -n "biere" -v 0.1.0 -p biere-1.0.deb