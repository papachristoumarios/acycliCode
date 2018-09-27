<center><h1>acycliCode</h1> </center>

<p align="center">

<img src="https://img.shields.io/packagist/l/doctrine/orm.svg"> <img src="https://img.shields.io/pypi/pyversions/Django.svg"><img src="https://img.shields.io/badge/lang-C-green.svg">

</p>

**acycliCode** is a library for detecting Layering Violations as part of Continuous Integration (CI) checks projects with a C codebase. It is built on Python 3.x and [GNU Cflow](https://www.gnu.org/software/cflow/) and follows a differential approach of cycle detections keeping layers in disjoint sets. It uses this approach to prevent the problem of layering violations from happening.  It features checking for layering violations using Cflow static flow graph generator. It is released under the MIT License. 