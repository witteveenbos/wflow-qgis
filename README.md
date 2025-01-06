# Description

### Projectname: @@
### Projectcode: @@
### Author: Peter van Tol

# Content
Describe what this repo does for the project.

# Quality
This project had code quality: @@

> W+B has a standard for calculations in code, see [standard for calculations in code](https://witteveenbos.sharepoint.com/:b:/r/sites/Innovating/SiteAssets/SitePages/Programming-Knowledge-Centre/memo-the_standard_for_calculations_in_code.pdf?csf=1&web=1&e=WGkRXL). This standard describes three code levels, and associated quality control requirements:
> 1. One or serveral scripts within 1 project with limited risk and limited chance of reuse.
> 2. Reusable functionality, to be used in multiple projects or functionality with significant risk.
> 3. Software (almost) continuously running or handed over to client.
>
> If your code is just for some testing, and has no quality then enter level 0.


# Project specific User Manual

> W+B is required to be able to recreate the results of a report, for several years
> after project delivery. Describe here how to recreate the results that we sent to the client.
> You should think of:
> - Which files did you run, did you use arguments
> - When did you run the file, wich version
> - If source data (KNMI-data, measurements, drawings) is used, where is it stored, which version did you use
> - If different branches are used for different variants, explain them
> - If there are unused/old files in this repo: remove them, or explain why they are still here
> - You can assume the user has already found this code on GitLab, and knows how to pull it.
>
> By using this template and `poetry` it is guaranteed that the project / environment can always
> be restated to its original state as it was left when archived.

Example:
- windcalculator.py from the main branch is used to calculate the maximum windload
  on the structure. It requires the knmi data from P:/123456/windmetingen_knmi, this
  path is defined in the file. In the first report there were errors, these were
  fixed in january 2022 with commit #eadbd
- the branch _some-variant-we-did-not-use_ contains a variant. We never delivered
  this, because of arbitrary reason, but they paid good money for it, and might want
  to use it for some other project.
- just before/after generating the report with id 123456-00-not01, all code was commited
  on 1 jan 2022 with commit #eadkl
- etc.

# Developer Quickstart manual
Here are some quick tips on working the poetry environment and development of the
script. For full documentation on how to use `poetry` and more advanced use-case,
please check ZenWorks.

## GitLab
You're probably reading this readme on GitLab. W+B/DKR has a policy to put all code
on the W+B gitlab server. This enables code-review and version-history. If you don't
know how to work with GitLab see the [manual version control](https://witteveenbos.sharepoint.com/:b:/r/sites/Innovating/SiteAssets/SitePages/Programming-Knowledge-Centre/100032-12-20-014.185-notd02-Introduction-GIT---English-version.pdf?csf=1&web=1&e=jdQ3zv).
We also have free internal courses on GitLab, you can find these courses on the HR internal courses page under the tab 'digital competences'.

## Installing the environment
If you have just created this script using the templates or pulled this script from
GitLab on an new PC you should run `poetry install` inside this folder to create an
isolated environment and install all required packages.

## Adding a package to your environment
Adding a package to the environment: `poetry add <package-name>`

Example for adding numpy:
`poetry add numpy`

Example for adding multiple packages simultaneously
`poetry add numpy pandas matplotlib`

Poetry automatically checks for packages on the internal pypi, so for an internal
package e.g. wbsphinx use:
`poetry add wbspinx`

> **NOTE:** A (VPN) connection  to the W+B network is required.
>
> To add packages it is required to be connected to the WB network (either by being
> in a WB office or by GlobalProtect VPN). When not connected an exception will be
> thrown by `poetry`

## Making the environment available in VScode
Go to the folder where this file is located and run:
`poetry run code .`
