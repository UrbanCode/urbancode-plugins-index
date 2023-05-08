# UrbanCode Plugins Index

This repository hosts the plug-in index for all UrbanCode products (UrbanCode Deploy - UCD, UrbanCode Velocity - UCV, UrbanCode Release - UCR, UrbanCode Build - UCB) and it is based on the UrbanCode/velocity-plugins-index repository. Text is copied from velocity-plugins-index README.

## Repository Structure

* `plugins`: A directory containing a list of sub directories for each product, which in self contains a list of directories per plugins by `pluginId`. Each plugin directory should have an `info.json` and `releases.json` file.

  * `info.json`: A file containing a JSON object of general information about the plugin that will help users identify if they want to install the plugin to their instance of UrbanCode xxx.
  * `releases.json`: A file containing a JSON array of release objects, each release object containing the information necessary to install the release and some optional notes to help users identify if they should upgrade to that plugin version in their instance of UrbanCode xxx.

* `index.json`: A file generated based on the `plugins` directory contents, containing a JSON object with keys for each `pluginId` and values containing the plugin general information and latest release information.

## Json Structure

There are 2 main file types that must abide by strict guidelines:

* `info.json`: A JSON object contains the following fields:

    | Field                  | Type   | Required | Description             |
    |------------------------|--------|----------|-------------------------|
    | name                   | string | yes      | The display name of the plugin. This is how users will identify the plugin in UrbanCode xxx.  |
    | docs_folder            | string | yes      | Documentation directory name |
    | docsURL                | string | yes      | A URL to a website containing information about the plugin. A user would use this information to find out more about the plugin |
    | plugin_files           | string | yes      | Plugin files directory |
    | description            | string | yes      | A short description about what the plugin does. This should provide enough context for a user to determine whether the plugin is right for their needs. |
    | specification          | object | yes      | Specifiying the plugin |
    | specification.category | string | yes      |  SCM; Source; Automation; ??? |
    | specification.type     | string | yes      |  Community (for opensource); Partner, IBM; ??? |
    | author                 | object | yes      | Who is responsible for creating/updating the plugin. This will let a user know who is responsible for maintaining the plugin. |
    | author.name            | string | yes      | The name of the author. If the plugin is tied to an organization, this should be the name of the organization. A user might check this name to ensure the plugin is written by a reliable source. |
    | author.email           | string | yes      | The email of the author. If the plugin is tied to an organization, this should be an email within the organization. A user might reach out to this email for support or to report a bug.          |

* `releases.json`: A JSON array whose objects have the following fields:

    | Field | Type | Required | Description |
    | ----- | ---- | -------- | ----------- |
    | version | string | yes | The version of the release, free form, can be equal to semver, but may not |
    | semver | string | yes | The version of the release, adhering to the [Semantic Versioning](https://semver.org/) standard. Must be unique per release object. |
    | date | string | yes | The date and time of the release, adhering to the [ISO 8601](https://web.archive.org/web/20171020085148/https://www.loc.gov/standards/datetime/ISO_DIS%208601-2.pdf) format. Must occur later than the previous release. |
    | file | string | yes | The file image of the plugin. Must exist in target repository with the exact same name. |
    |      |        |     | If a docker image then exact image name, must also exisit on registry. |
    |      |        |     | If OSS file, URL to the release file |
    | notes | array | yes | An array of strings containing notes of what the new release introduces for the plugin (bug fixes, features, etc). May be an empty array to omit notes. |
    | supports | string | no | The minimum version of UrbanCode PRODUCT that the release is compilable with, adhering to the [Semantic Versioning](https://semver.org/) standard. |

## Install Dependencies

## Generate index.json

## Linting

## Adding A New Plugin

## Releasing A New Plugin Version
