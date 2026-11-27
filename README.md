# Omarchy on a 2009 iMac

Field notes and patches for Omarchy on a Late 2009 iMac (iMac10,1), including a Chromium Wayland rendering fix.

The stock installer showed four copies of the boot splash. R2 brought the built-in panel up at 1920×1080. We made room on the 1 TB internal disk by shrinking the High Sierra HFS+ volume, kept the original EFI and Recovery partitions, and installed Omarchy from the built-in SD slot. High Sierra booted after the first installation attempt. Its boot after the final installation is still unverified.

Read the field notes in [English](https://dueyama.github.io/omarchy-imac-field-notes/) or [日本語](https://dueyama.github.io/omarchy-imac-field-notes/ja.html).

## Chromium Wayland Readback

The patch targets Linux x86_64 with Ozone Wayland. It synchronously reads back the composited GL frame and presents it through Wayland shared memory (`wl_shm`). The feature is disabled by default. To enable it for comparison, pass `--enable-features=WaylandGLReadbackPresentation`.

| Item | Value |
| --- | --- |
| Target version | Chromium `155.0.8059.84` |
| Base commit | `5869fe313571d75152b77813cf0a4ee26a4e6df0` |
| 1. Shared-memory presentation | [wayland-gl-readback.patch](docs/patches/chromium-155.0.8059.84/wayland-gl-readback.patch) |
| Patch 1 SHA-256 | `7a60eff3abaf9aff26be1dd34f61698168af0f4f7ce65e96f83a7df9cff1defa` |
| 2. EGL configuration for the Radeon readback buffer | [readback-pbuffer-v2.patch](docs/patches/chromium-155.0.8059.84/readback-pbuffer-v2.patch) |
| Patch 2 SHA-256 | `c746ffa26d2a8a27793fc0658e51ed2a10b976168c6511a86e583f31097d389d` |
| Build settings | [args.gn](docs/patches/chromium-155.0.8059.84/args.gn) |
| Upstream copyright notice | [Chromium LICENSE](docs/patches/chromium-155.0.8059.84/LICENSE.chromium) |

Run these commands from the Chromium source tree at the base commit. Use a prepared Chromium checkout with the matching toolchain, dependencies and Linux x64 sysroot. Apply both patches in the order below. Replace `/path/to/patches` with the path to the patch and settings. [Chromium Linux build instructions](https://chromium.googlesource.com/chromium/src/+/5869fe313571d75152b77813cf0a4ee26a4e6df0/docs/linux/build_instructions.md)

```sh
(cd /path/to/patches && sha256sum -c SHA256SUMS)
git apply --check /path/to/patches/wayland-gl-readback.patch
git apply /path/to/patches/wayland-gl-readback.patch
git apply --check /path/to/patches/readback-pbuffer-v2.patch
git apply /path/to/patches/readback-pbuffer-v2.patch
mkdir -p out/imac-wayland
cp /path/to/patches/args.gn out/imac-wayland/args.gn
buildtools/linux64/gn gen out/imac-wayland --fail-on-unused-args
third_party/ninja/ninja -C out/imac-wayland chrome chrome_sandbox
```

The iMac ran Readback v2 under native Wayland with Radeon GPU compositing and WebGL enabled. In six static captures and eight scroll positions, only the pointer region differed at the test threshold. The GPU process recorded zero crashes during the test. The patched build became the default browser. The [video measurements](docs/index.html#youtube) record later H.264 test builds, the cost of full-frame readback, and the partial-readback experiment. Long-term stability is still pending.

The Radeon panel correction and Hyprland border shader fix came from an earlier project. The [patch provenance](https://dueyama.github.io/omarchy-imac-field-notes/#provenance) section links to the exact revisions used here.

## GitHub Pages

The publication source for `dueyama/omarchy-imac-field-notes` is the generated HTML in `docs/`. In Pages settings, choose **Deploy from a branch**, then **`main`** and **`/docs`**. GitHub Pages serves the generated HTML directly. [Configuring a publishing source for GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)

Edit `content.json` and run `python3 build.py --site-url https://dueyama.github.io/omarchy-imac-field-notes/` to regenerate both languages with their canonical and social preview URLs. List diary chapters by date, oldest first, and keep reference material in the final chapter. The `chapters` lists set the reading order for both the article and its contents. Keep existing section IDs when moving a note so its links continue to work.

The migration starts from published version 9 (`0d8803b53c362119818809c76f2120e3817d695e`). Before updating the notice on the original site, check language switching, both photos, and the patch download on the new URL. [Original ChatGPT Sites field notes](https://omarchy-imac-field-notes.dueyama.chatgpt.site/)
