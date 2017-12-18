esdata
=====

Interface to the REST API providing access to _Eurostat_ online database.
---

**About**

This module will enable you to automatically query, search, download and handle data from the [online database](http://ec.europa.eu/eurostat/data/database) of [_Eurostat_](http://ec.europa.eu/eurostat/).

<table align="center">
    <tr> <td align="left"><i>documentation</i></td> <td align="left">available at: https://gjacopo.github.io/esdata/</td> </tr> 
    <tr> <td align="left"><i>since</i></td> <td align="left">2017</td> </tr> 
    <tr> <td align="left"><i>license</i></td> <td align="left"><a href="https://joinup.ec.europa.eu/sites/default/files/eupl1.1.-licence-en_0.pdfEUPL">EUPL</a> </td> </tr> 
</table>


**<a name="Description"></a>Description**

**<a name="Notes"></a>Notes**

* The Web Services have some limitation as to the supported for a request since currently a maximum of 50 "categories", _e.g._ a message "Too many categories have been requested. Maximum is 50." is returned in case of a too large request (see the data scope and query size limitation [here](http://ec.europa.eu/eurostat/web/json-and-unicode-web-services/data-scope-and-query-size)). This limitation is bypassed by the use of the `esdata` package.

**<a name="Sources"></a>_Eurostat_ sources**

* Database: online catalog](http://ec.europa.eu/eurostat/data/database) and [bulk download facility](http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing).
* Web-services: access to [JSON and unicode data](http://ec.europa.eu/eurostat/web/json-and-unicode-web-services/about-this-service), the [REST API](http://ec.europa.eu/eurostat/web/json-and-unicode-web-services/getting-started/rest-request) with its [query builder](http://ec.europa.eu/eurostat/web/json-and-unicode-web-services/getting-started/query-builder).
* Standard code lists: [RAMON](http://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM&StrGroupCode=SCL&StrLanguageCode=EN) metadata.

**<a name="References"></a>Tools and references**

* Lahti L., Huovari J., Kainu M., and Biecek, P. (2017): [**Retrieval and analysis of Eurostat open data with the eurostat package**](https://journal.r-project.org/archive/2017/RJ-2017-019/RJ-2017-019.pdf), _The R Journal_, 9(1):385-392.
* `R` package [_eurostat_ `R`](http://ropengov.github.io/eurostat) access open data from Eurostat.
* `Java` library [_java4eurostat_](https://github.com/eurostat/java4eurostat) for multi-dimensional data manipulation.
* `Python` library [_wbdata_](https://github.com/OliverSherouse/wbdata) for accessing World Bank data.
* Lightweight dissemination format [_JSON-stat_](https://json-stat.org).
