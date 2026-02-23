<!-- source: https://docs.manim.community/en/stable/installation/conda.html -->

# Conda

## Required Dependencies

There are several package managers that work with conda packages,
namely [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html),
[mamba](https://mamba.readthedocs.io) and [pixi](https://pixi.sh).

After installing your package manager, you can create a new environment and install `manim` inside by running

conda / mamba

```python
# if you want to use mamba, just replace conda below with mamba
conda create -n my-manim-environment
conda activate my-manim-environment
conda install -c conda-forge manim
```


pixi

```python
pixi init
pixi add manim
```

Since all dependencies (except LaTeX) are handled by conda, you don’t need to worry
about needing to install additional dependencies.

## Optional Dependencies

In order to make use of Manim’s interface to LaTeX to, for example, render
equations, LaTeX has to be installed as well. Note that this is an optional
dependency: if you don’t intend to use LaTeX, you don’t have to install it.

Recommendations on how to install LaTeX on different operating systems
can be found [in our local installation guide](uv.html).

## Working with Manim

At this point, you should have a working installation of Manim, head
over to our [Quickstart Tutorial](../tutorials/quickstart.html) to learn
how to make your own *Manimations*!
