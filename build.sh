#!/bin/bash

set -e

flatpak-builder --user --install --force-clean build-dir localtest.yaml
flatpak run io.github.schwarzen.colormydesktop
