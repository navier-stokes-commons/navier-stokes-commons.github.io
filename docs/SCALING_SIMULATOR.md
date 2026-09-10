# Scaling simulator

The homepage scaling simulator is a public scientific explorable built from the leading-order inner-core relations stated in Section 2.1 of OpenAI's paper *Finite time blowup for Navier-Stokes*.

Its canonical machine-readable input is `content/public/scaling_model.json`. The deployed copy is advertised by `.well-known/commons.json`; resolve its relative `scaling_model` reference against the discovery document URL.

With `tau = 1 - t` and `0 < h < 1/100`, the model records these characteristic relations:

```text
ell_r        asymp  tau^(1/2)
ell_z        asymp  tau^(1/2-h)
|u_theta|    asymp  tau^(-1/2-h)
|u_z|        asymp  tau^(-1/2-h)
|u_r|        O      tau^(-1/2)
volume       order  tau^(3/2-h)
E_core       order  tau^(1/2-3h)
Re_theta     asymp  tau^(-h)
ell_z/ell_r asymp  tau^(-h)
```

The interactive uses normalized values with unspecified positive multiplicative constants set to 1. This allows exact exploration of the exponents and ratios without inventing absolute physical units.

## Representations

The same canonical model drives:

- precomputed numeric values in HTML;
- precomputed SVG log-scale curves;
- normalized core aspect geometry;
- static ASCII frames;
- an interactive JavaScript time and `h` explorer;
- the public JSON endpoint.

JavaScript is optional. If JavaScript is unavailable, the page still contains the formulas, source link, numeric table, plotted curves, core aspect, and ASCII sequence.

## Scientific boundary

The simulator evaluates the published asymptotic scaling model. It is not a numerical integration of the full three-dimensional Navier-Stokes PDE. A future CFD module must have its own equations, discretization, convergence evidence, and validation metadata before it can be presented as a numerical PDE simulation.
