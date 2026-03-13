Dash docset generator for [Meson](https://mesonbuild.com/)

### Instructions

- Download and build docs from
[upstream source](https://github.com/mesonbuild/meson)
    - Follow instructions here
    [here](https://github.com/mesonbuild/meson/blob/master/docs/README.md)

- `meson-dash-docset-generator MANUAL_SOURCE`

    - If `pipx` is installed, you can avoid `pip install`ing anything and just
    run `pipx run meson-dash-docset-generator MANUAL_SOURCE`
    - `MANUAL_SOURCE` will be the path to the html sources, which 
    should be something like `built_docs/Meson documentation-doc/html`
    - For a full set of options: `meson-dash-docset-generator -h`
