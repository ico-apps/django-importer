# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## master

## [0.4.0] - 2022-07-06
- [added] #48 CachedSlugRelatedField: optimize DB queries (1 big vs N small)
- [fixed] #49 CachedSlugRelatedField produces cross dependencies
- [fixed] #51 Build setup config.

## [0.3.0] - 2021-11-28
- [added] `log` attribute to CSV models.
- [added] Implement append mode. If enabled, existing objects will be ignored.
- [fixed] #14 Detect CSV file encoding.
- [fixed] #43 Handle unexpected errors.

## [0.2.0] - 2021-05-26
- [changed] Show human-friendly error messages.
- [changed] Optimize speed.

## [0.1.0] - 2021-05-10
- [added] Support passing delimiter and headers mapping as parameters.

## [0.0.1] - 2021-03-15
- First beta release.
