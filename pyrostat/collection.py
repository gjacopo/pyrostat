# -*- coding: utf-8 -*-

"""
.. collection.py

Basic class used for the definition and retrieval of online collections, e.g. 
dimensions and datasets, from `Eurostat online database <http://ec.europa.eu/eurostat>`_.

**About**

*credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 

*version*:      0.1
--
*since*:        Wed Jan  4 01:57:24 2017

**Description**


**Usage**

    >>> from collection import Collection
    
**Dependencies**

*call*:         :mod:`settings`, :mod:`request`, :mod:`collections`

*require*:      :mod:`os`, :mod:`sys`, :mod:`string`, :mod:`warnings`, \ 
                :mod:`itertools`, :mod:`collections`, :mod:`numpy`
                
*optional*:     :mod:`pandas`, :mod:`lxml`

**Contents**
"""


#==============================================================================
# IMPORT STATEMENTS
#==============================================================================

import os
import warnings
import string
from itertools import zip_longest
from collections import OrderedDict

import numpy as np

try:
    import pandas as pd
except ImportError:     
    pd = None     

try:                                
    import lxml
except ImportError:                 
    pass

from . import pyroWarning, pyroError
from . import settings
from . import session

#==============================================================================
# CLASSES/METHODS
#==============================================================================
    
#%%
class __Base(object):
    """Generic collection class.
    """
    #/************************************************************************/
    def __init__(self, **kwargs):
        """Initialisation of a :class:`Collection` instance; pass all domain/query
        items and  set all session.

            >>> coll = Collection(**kwargs)
            
        Keyword Arguments for url query
        -------------------------------
        `domain` : str
            keys used to set various credentials, e.g. key, secret, token, and t
        `query` : str
        `lang` : str
        `sort` : int
        
        Keyword Arguments used for :mod:`session` setting
        -------------------------------------------------  
        `cache`: str
            directory where to store downloaded files
        `time_out`: 
            number of seconds considered to store file on disk, None is infinity, 
            0 for not to store; default
        `force_download` : bool
        """
        # set default values
        self._domain       = ''
        self._query        = ''
        self._lang         = settings.DEF_LANG
        if kwargs != {}:
            attrs = [a[1] if len(a)>1 else a for a in [attr.split('_') for attr in self.__dict__]] 
            # ( 'domain','query','lang')
            for attr in list(set(attrs).intersection(kwargs.keys())):
                try:
                    setattr(self, '_{}'.format(attr), kwargs.pop(attr))
                except: 
                    warnings.warn(pyroWarning('wrong attribute value {}'.format(attr.upper())))
        self._session      = None
        self._url          = None
        self._status       = None
        self.setSession(**kwargs)   # accepts keywords: time_out, force_download, cache
        self.setURL(**kwargs)       # accepts keywords: query, sort
       
    #/************************************************************************/
       
    #/************************************************************************/
    def setURL(self, **kwargs):
        """Set the query URL to *Bulk download* web service.
        
            >>> url = C.setURL(**kwargs)
           
        Keyword Arguments
        -----------------
        kwargs : dict
            define the parameters for web service.
                
        Returns
        -------
        url : str
            link to Eurobase web service to submit the specified query.

        Note
        ----
        The generic url formatting is:
    
        Example: 
            http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?dir=comp
            http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&dir=dic

        # DIC_URL         = 'ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&dir=dic'
        # DATA_URL        = 'ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&dir=data'
    
        """
        if 'lang' in  kwargs:   kwargs.pop('lang')
        #[kwargs.update({attr: kwargs.get(attr) or getattr(self, '{}'.format(attr))})
        #    for attr in ('query','sort')]
        kwargs.update({'query': kwargs.get('query') or self.query})
        self.__url = Session.build_url(self.domain, **kwargs)
    def getURL(self, **kwargs):
        # update/merge passed arguments with already existing ones
        if 'lang' in  kwargs:   kwargs.pop('lang')
        #[kwargs.update({attr: kwargs.get(attr) or getattr(self, '{}'.format(attr))})
        #    for attr in set(('query','sort')).intersection(set(kwargs.keys()))]
        if kwargs != {}:
            kwargs.update({'query': kwargs.get('query') or self.query})
        return Session.build_url(self.domain, **kwargs) or self.url
    @property
    def url(self):
        #if self._url is None:   self.setURL()
        return self._url

    #/************************************************************************/
    def setSession(self, **kwargs):
        """Set the session of the :class:`{Collection}` instance.
        
            >>> session = C.setSession(**kwargs)
        """
        try:
            self._session = sessionSession(**kwargs)
        except:
            raise pyroError('wrong definition for SESSION parameter')
    def getSession(self, **kwargs):
        """Retrieve the session of the :class:`{Collection}` instance, or define
        a new one when arguments are passed.
        
            >>> session = C.getSession(**kwargs)

        """
        try:
            session = Session(**kwargs)
        except:
            session = None
            pass
        return session or self._session
    @property
    def session(self):
        return self._session #.session

    #/************************************************************************/
    @property
    def domain(self):
        """Domain attribute (:data:`getter`/:data:`setter`) used through a session 
        launched to connect to bulk data webservice or REST service. 
        """
        return self._domain
    @domain.setter#analysis:ignore
    def domain(self, domain):
        if not isinstance(domain, str):
            raise pyroError('wrong type for DOMAIN parameter')
        self._domain = domain

    #/************************************************************************/
    @property
    def query(self):
        """Query attribute (:data:`getter`/:data:`setter`) attached to the domain
        and used througout a launched session. 
        """
        return self._query
    @query.setter
    def query(self, query):
        if not isinstance(query, str):
            raise pyroError('wrong type for QUERY parameter')
        self._query = query

    #/************************************************************************/
    @property
    def lang(self):
        """Attribute (:data:`getter`/:data:`setter`) defining the language of the
        objects (urls and files) returned when connecting througout a session. 
        See :data:`settings.LANGS` for the list of currently accepted languages. 
        """
        return self._lang
    @lang.setter
    def lang(self, lang):
        if not isinstance(lang, str):
            raise pyroError('wrong type for LANG parameter')
        elif not lang in settings.LANGS:
            raise pyroError('language not supported')
        self._lang = lang
       
    #/************************************************************************/
    @staticmethod
    def _fileexists(file):
        return os.path.exists(os.path.abspath(file))
       
    #/************************************************************************/
    def _url_static(self, **kwargs):
        if kwargs == {}:
            return domain
        # set parameters
        if 'lang' in kwargs:    lang = kwargs.pop('lang')
        else:                   lang = None
        if lang is not None and lang not in settings.LANGS:
            raise pyroError('language not supported')
        # bug with the API? note that 'sort' needs to be the first item of the 
        # filters
        if 'sort' in kwargs:    sort = kwargs.pop('sort')
        else:                   sort = settings.DEF_SORT
        kwargs = OrderedDict(([('sort',sort)]+list(kwargs.items())))
        # see also https://www.python.org/dev/peps/pep-0468/ 
        url = Session.build_url(domain, **kwargs)
        if lang is not None:
            url = "{url}/{lang}".format(url=url,lang=lang)
        return url
        

rest
{host_url}/rest/data/{version}/{format}/{language}/{datasetCode}?{filters}
http://ec.europa.eu/eurostat/wdds/ rest/data/v2.1/ json/en/nama_gdp_c?precision=1&geo=EU28&unit=EUR_HAB&time=2010&time=2011&indic_na=B1GM


metabase:
http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/ BulkDownloadListing? sort=1&file=metabase.txt.gz
toc:
http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/ BulkDownloadListing?sort=1&file=table_of_contents_en.txt
dimension (dictionary):
http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/ BulkDownloadListing?sort=1&file=dic%2Fen%2Fage.dic
dataset:
http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/ BulkDownloadListing?sort=1&file=data%2Filc_di01.tsv.gz
http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/ BulkDownloadListing?sort=1&file=data%2Faact_ali01.tsv.gz
metadata:
http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/ BulkDownloadListing?sort=1&file=metadata%2Faact_esms.sdmx.zip

    
#%%
class Bulk(__Base):
    """
    http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=dic/en/net_seg10.dic    
    http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=dic/en/dimlist.dic    

    dimensions:
    http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=dic/en/net_seg10.dic    
    http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=dic/en/dimlist.dic    
 
    datasets:
    http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?dir=data&sort=1&start=a
    http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=metabase.txt.gz
    """
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        """Initialisation of a :class:`Collection` instance; pass all domain/query
        items and  set all session.

            >>> x = Collection(**kwargs)
            
        Keyword Arguments
        -----------------  
        `domain` : str
            keys used to set various credentials, e.g. key, secret, token, and t
        `query` : str
        `lang` : str
        `sort` : int
        `dimension` :
        `dataset` :
        
        Keyword Arguments used for :mod:`session` setting
        -------------------------------------------------  
        `cache`: str
            directory where to store downloaded files
        `time_out`: 
            number of seconds considered to store file on disk, None is infinity, 
            0 for not to store; default
        `force_download` : bool
        """
        # set default values
        self._domain       = settings.BULK_DOMAIN
        self._sort         = settings.DEF_SORT
        self._query        = settings.BULK_QUERY
        self._dimension    = {}
        self._dataset      = {} # dict([(a, []) for a in list(string.ascii_lowercase)])
        # update
        super(self, Bulk).__init__(**kwargs)
        
    #/************************************************************************/
    @property
    def sort(self):
        """Sort attribute (:data:`getter`/:data:`setter`) used througout a session 
        launched to query _Eurostat_ bulk data collection. 
        """
        return self._sort
    @sort.setter
    def sort(self, sort):
        if not isinstance(sort, int):
            raise pyroError('wrong type for SORT parameter')
        elif not sort > 0:
            raise pyroError('wrong value for SORT parameter')
        self._sort = sort

    #/************************************************************************/
    @property
    def metabase(self):
        """Metabase attribute (:data:`getter`/:data:`setter`) storing, in a table,
        the information of _Eurostat_ bulk download metabase.
        """
        return self.__metabase
    @metabase.setter
    def metabase(self, metabase):
        if isinstance(metabase, np.array):
            if pd is not None:
                metabase = pd.DataFrame(data=metabase)
            else:
                pass
        elif not isinstance(metabase, pd.DataFrame):
            raise pyroError('wrong value for METABASE parameter')
        self.__metabase = metabase

    #/************************************************************************/
    @property
    def toc(self):
        """TOC attribute (:data:`getter`/:data:`setter`) storing, the table of 
        contents hosted on _Eurostat_ bulk download metabase.
        """
        return self.__toc
    @toc.setter
    def toc(self, toc):
        if isinstance(toc, np.array):
            if pd is not None:
                toc = pd.DataFrame(data=toc)
            else:
                pass
        elif not isinstance(toc, pd.DataFrame):
            raise pyroError('wrong value for TOC parameter')
        self.__toc = toc

    #/************************************************************************/
    @property
    def dimension(self):
        """Dimension attribute (:data:`getter`/:data:`setter`) storing, in a 
        dictionary, the dimensions (dictionary fields) that have been loaded from
        the _Eurostat_ bulk download website.
        """
        return self.__dimension.keys()
    @dimension.setter
    def dimension(self, dimension):
        #if isinstance(dimension, dict):    do nothing 
        if isinstance(dimension, (list,tuple)):
            dimension = dict(zip_longest(list(dimension),None))
        elif isinstance(dimension, str):
            dimension = {dimension: None}
        if not isinstance(dimension, dict) or not all([isinstance(d,str) for d in dimension]):
            raise pyroError('wrong type for DIMENSION parameter')       
        self.__dimension = dimension # not an update!

    #/************************************************************************/
    @property
    def dataset(self):
        """Dataset attribute (:data:`getter`/:data:`setter`) storing, in a 
        dictionary, the datasets (dictionary fields) that have been loaded from
        the *Eurostat bulk download* website in the :class:`{Collection}` instance.
        """
        # return [items for lists in self.__dataset.values() for items in lists]
        return self.__dataset.keys()
    @dataset.setter
    def dataset(self, dataset):
        # if isinstance(dataset, dict):   do nothing
        if isinstance(dataset, (list,tuple)):
            dataset = dict(zip_longest(list(dataset),None))
        elif isinstance(dataset, str):
            dataset = {dataset: None}
        if not isinstance(dataset, dict) or not all([isinstance(d,str) for d in dataset]):
            raise pyroError('wrong type for DATASETS parameter')       
        self.__dataset = dataset # not an update!
 
    #/************************************************************************/
    @staticmethod
    def update_url(domain, **kwargs):
        """Build (update) an URL using a predefined URL (e.g., a domain) and a set
        of query arguments encoded as key/value pairs.
        
            >>> url = C.update_url(domain, **kwargs)
         
        Argument
        --------
        url : str
            basic url path to be extended.
           
        Keyword Arguments
        -----------------  
        kwargs : dict
            any other regularly query arguments to be encoded in the url path, e.g.,
            in something like :data:`key=value` where :data:`key` and :data:`value` 
            are actually the key/value pairs of :data:`kwargs`; among other possible
            queries, :data:`sort` and :data:`lang` are accepted; note that :data:`lang` 
            is used to set the language subdomain; when passed (i.e. :data:`lang` is
            not :data:`None`), the path of the url will be extended with the language
            value: :data:`url/lang`.
            
        Returns
        -------
        url : str
            url path of the form :data:`domain/{query}
            
        See also
        --------
        :meth:`Session.build_url`
        """
        if kwargs == {}:
            return domain
        # set parameters
        if 'lang' in kwargs:    lang = kwargs.pop('lang')
        else:                   lang = None
        if lang is not None and lang not in settings.LANGS:
            raise pyroError('language not supported')
        # bug with the API? note that 'sort' needs to be the first item of the 
        # filters
        if 'sort' in kwargs:    sort = kwargs.pop('sort')
        else:                   sort = settings.DEF_SORT
        kwargs = OrderedDict(([('sort',sort)]+list(kwargs.items())))
        # see also https://www.python.org/dev/peps/pep-0468/ 
        url = Session.build_url(domain, **kwargs)
        if lang is not None:
            url = "{url}/{lang}".format(url=url,lang=lang)
        return url
            
    #/************************************************************************/
    def last_update(self, **kwargs):
        """Retrieve the time a table (dictionary or dataset) was last updated.
        """
        dimension, dataset = [kwargs.get(key) for key in ('dic','data')]
        if dataset is None and dimension is None:
            raise pyroError('one of the parameters DIC or DATA needs to be set')
        elif not(dataset is None or dimension is None):
            raise pyroError('parameters DIC or DATA are incompatible')
        if dimension is not None:
            df = self.loadTable('dic')
            kname, kdate = [settings.BULK_DIC_NAMES.get(key) for key in ('Name','Date')]
        else:
            df = self.loadTable('data', alpha=dataset[0])
            kname, kdate = [settings.BULK_DATA_NAMES.get(key) for key in ('Name','Date')]
        try:
            names = [d.split('.')[0] for d in list(df[0][kname])]
            dates = [d.split('.')[0] for d in list(df[0][kdate])]
        except:
            raise pyroError('impossible to read {}/{} columns of bulk table'.format(kname,kdate)) 
        try:
            ipar = names.index(dataset or dimension)
        except:
            raise pyroError('entry {} not found in bulk table'.format(dataset or dimension)) 
        else:
            date = dates[ipar]
        return date

    #/************************************************************************/
    def readTable(self, key, alpha='a'):
        df = None
        kwargs = {'skiprows': [1], 'header': 0}
        bulk_dir = settings.__builtins__['BULK_{}_DIR'.format(key)]
        url = self.update_url(self.url, sort=self.sort, dir=bulk_dir)
        if key == 'dic':
            # note that alpha is ignored
            url = '{}/{}'.format(url, self.lang)
        elif key == 'data':
            if alpha not in list(string.ascii_lowercase):
                raise pyroError('wrong parameter ALPHA')
            url = '{url}&start={alpha}'.format(url=url, alpha=alpha)        
        try:
            df = self.session.read_html_table(url, **kwargs)
        except:
            raise pyroError('impossible to read html table: {}'.format(url)) 
        return df
    def loadTable(self, key, alpha='a'):
        if not key in ('dic','data'):
            raise pyroError('keyword parameter {} not recognised'.format(key))
        elif key == 'dic':
            if not hasattr(self.__dimension, '_table_'):
                self.__dimension['_table_'] = self.readTable(key)
            return self.__dimension['_table_']
        else:
            if not hasattr(self.__dataset, '_table_')                      \
                and  not hasattr(self.__dataset['_table_'], alpha):
                    self.__dataset['_table_'][alpha] = self.readTable(key, alpha)
            return self.__dataset['_table_'][alpha]
    def read(self, **kwargs):
        """
        dimension example:
        example http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=dic%2Fen%2Faccident.dic

        dataset example: 
        http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=data%2Faact_ali01.tsv.gz
        http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=data%2Faact_ali01.sdmx.zip     
        """
        try:    dimension = kwargs.pop('dic')
        except: dimension = None
        else:   key, entity = 'DIC', 'dimension'
        try:    dataset = kwargs.pop('data')
        except: dataset = None
        else:   key, entity = 'DATA', 'dataset'
        if dataset is None and dimension is None:
            raise pyroError('one of the parameters DIC or DATA needs to be set')
        elif not(dataset is None or dimension is None):
            raise pyroError('parameters DIC or DATA are incompatible')
        bulk_exts = settings.__builtins__['BULK_{}_EXTS'.format(key)]
        bulk_zip = settings.__builtins__['BULK_{}_ZIP'.format(key)]
        bulk_dir = settings.__builtins__['BULK_{}_DIR'.format(key)]
        try:
            ext = kwargs.pop('ext')
        except:
            ext = bulk_exts[0]
        else:
            if ext not in bulk_exts:   
                raise pyroError('bulk {} extension EXT not recognised'.format(key)) 
        if bulk_zip != '':
            ext = '{ext}.{zip}'.format(ext=ext, zip=bulk_zip)
        try:
            resp = getattr(self, 'check_{}'.format(entity))(dimension or dataset)
        except: 
            pass
        else:
            if resp is False:
                raise pyroError('wrong {}'.format(key)) 
        url = self.update_url(self.url, sort=self.sort, file=bulk_dir)
        if dimension is not None:
            url = '{}/{}'.format(url, self.lang)
        url = '{}/{}.{}'.format(url, dimension or dataset, ext)
        pathname, html = self.session.load_page(self, url, **kwargs)
        return pathname, html

    #/************************************************************************/
    @property
    def dataset(self):
        datasets = []
        # url = self.update_url(self.url, sort=self.sort, dir=settings.BULK_DATA_DIR)
        # kwargs = {'skiprows': [1], 'header': 0}
        kname = settings.BULK_DATA_NAMES['Name']
        for alpha in list(string.ascii_lowercase):
            try:
                df = self.loadTable('data', alpha=alpha)
            except:
                warnings.warn(pyroWarning('impossible to read html table: {}'.format(alpha)))
            else:
                # note the call to df[0] since there is one table only in the page
                datasets += [d.split('.')[0] for d in list(df[0][kname])]
        return datasets

    #/************************************************************************/
    @property
    def dimension(self):
        df = self.loadTable('dic')
        kname = settings.BULK_DIC_NAMES['Name']
        try:
            # note the call to df[0] since there is one table only in the page
            dimensions = [d.split('.')[0] for d in list(df[0][kname])]
        except:
            raise pyroError('impossible to read {} column of bulk table'.format(kname)) 
        return dimensions

    @property
    def __obsolete_bulk_dataset(self):
        datasets = []
        url = self.update_url(self.url, sort=self.sort, dir=settings.BULK_DATA_DIR)
        for alpha in list(string.ascii_lowercase):
            urlalpha = '{url}&start={alpha}'.format(url=url, alpha=alpha)
            _, html = self.session.load_page(urlalpha)
            if html is None or html == '':
                raise pyroError('no HTML content found') 
            _, rows = self.session.read_soup_table(html, attrs={'class':'filelist'})
            datasets += [d.split('.')[0] for d in self.__filter_table(rows)]
        return datasets
    @property
    def __obsolete_bulk_dimension(self):
        url = self.update_url(self.url, lang=self.lang, sort=self.sort, dir=settings.BULK_DIC_DIR)
        _, html = self.session.load_page(url)
        if html is None or html == '':
            raise pyroError('no HTML content found') 
        _, rows = self.session.read_soup_table(html, attrs={'class':'filelist'})
        dimensions = [d.split('.')[0] for d in self.__filter_table(rows)]
        return dimensions
    @staticmethod
    def __obsolete__filter_table(rows):
        rows = rows[0] # only one table in the page
        data, i = [], 0
        for row in rows:
            i = i+1
            try:                        cols = row.find_all("td")
            except:                     cols = row.findAll("td")
            if cols == [] or i <= 2:    continue
            else:                       data.append(cols[0].find('a').find(text=True))
        return data    
        
class Meta(__Base):
        
    #/************************************************************************/
    @property
    def dataset(self):
        if self.metabase is None:
            raise pyroError('no METABASE data found') 
        dataset = settings.BULK_BASE_NAMES['data']
        return self.metabase[dataset].unique().tolist()

    #/************************************************************************/
    @property
    def dimension(self):
        if self.metabase is None:
            raise pyroError('no METABASE data found') 
        dimension = settings.BULK_BASE_NAMES['dic']
        return self.metabase[dimension].unique().tolist()
    
    #/************************************************************************/
    def __getitem__(self, item):
        if not isinstance(item, str):
            raise pyroError('wrong type for ITEM parameter')
        if item in self.dimension:
            return self.__dimension[item]
        elif item in self.dataset:
            return self.__dataset[item]
    def __setitem__(self, item, value):
        if not isinstance(item, str):
            raise pyroError('wrong type for ITEM parameter')
        if item in self.dimension:
            self.__dimension[item] = value
        elif item in self.dataset:
            self.__dataset[item] = value
    def __contains__(self, item):
        if not isinstance(item, str):
            raise pyroError('wrong type for ITEM parameter')
        return item in self.dimension or item in self.dataset

    #/************************************************************************/
    @staticmethod
    def __check_member(member, members):
        if members is None or members==[]:
            raise pyroError('no members to compare to')
        if member in members:      
            return True
        else:                       
            return False
    def check_dimension(self, dimension):
        return self.__check_member(dimension, self.dimension)
    def check_dataset(self, dataset):
        return self.__check_member(dataset, self.dataset)
    
    #/************************************************************************/
    @staticmethod
    def __get_member(member, metabase, **kwargs):
        if metabase is None:
            raise pyroError('metabase data not found - load the file from Eurobase')
        members = settings.BULK_BASE_NAMES # ('data', 'dic', 'label')
        if member not in members:
            raise pyroError('member value not recognised - '
                                'must be any string in: {}'.format(members.keys()))
        elif set(kwargs.keys()).intersection([member]) != set(): # not empty
            raise pyroError('member value should not be passed as a keyword argument')
        grpby = list(set(kwargs.keys()).intersection(set(members)))
        if grpby != []:
            fltby = tuple([kwargs.get(k) for k in grpby]) # preserve the order
            if len(grpby) == 1:
                grpby, fltby = grpby[0], fltby[0]
            group = metabase.groupby(grpby).get_group(fltby)
        else:
            group = metabase
        return group[member].unique().tolist()
    @staticmethod
    def __set_member(member, **kwargs):
        pass
    
    #/************************************************************************/
    def getDataset(self, dataset):
        return self.__get_member('dic', self.metabase, data=dataset)
    def getDimension(self, dimension):
        return self.__get_member('label', self.metabase, dic=dimension)
    def setDataset(self, dataset):
        self.__datasets.update({dataset: self.getDataset(dataset)})
    def setDimension(self, dimension):
        self.__dimensions.update({dimension: self.getDimension(dimension)})

    #/************************************************************************/
    def getAllDatasets(self, dimension = None):
        """Retrieve all the datasets that are using a given dimension.
        """
        if dimension is None:
            return self.__get_member('data', self.metabase)
        else:
            return self.__get_member('data', self.metabase, dic=dimension)
    def getAllDimensions(self, dataset):
        """Retrieve all the dimensions used to define a given dataset.
        """
        return self.__get_member('dic', self.metabase, data=dataset)
    def getAllLabels(self, dimension, **kwargs):
        """Retrieve all the labels of a given dimension and possibly used
        by a given dataset.
        """
        return self.__get_member('label', self.metabase, dic=dimension, **kwargs)
 
    #/************************************************************************/
    def checkDataset(self, dataset):
        """Check whether a dataset exists in Eurostat database.
        
        Argument
        --------
        name : str
            string defining a dataset.
            
        Returns
        -------
        res : bool
            boolean answer (`True`/`False`) to the existence of the dataset `name`.
        """
        # return dataset in self.getAllDatasets(dimension)
        return dataset in self.getAllDatasets()
    def checkDimensionInDataset(self, dimension, dataset):
        """Check whether some dimension is used by a given dataset.
        """
        # return dataset in self.getAllDatasets(dimension)
        return dimension in self.getAllDimensions(dataset)
    def checkLabelInDimension(self, label, dimension, **kwargs):
        """Check whether some label is used by a given dimension.
        """
        return label in self.getAllLabels(dimension, **kwargs)
        
    #/************************************************************************/
    @property
    def geocode(self):
        return self.getDimension('geo')
        
    #/************************************************************************/
    def setMetabase(self, **kwargs):
        self.__metabase = self.readMetabase(**kwargs)
    def readMetabase(self, **kwargs):
        basefile = '{base}.{ext}'.format(base=settings.BULK_BASE_FILE, ext=settings.BULK_BASE_EXT)
        if settings.BULK_BASE_ZIP != '':
            basefile = '{base}.{zip}'.format(base=basefile, zip=settings.BULK_BASE_ZIP)
        url = self.update_url(self.url, sort=self.sort, file=basefile)
        kwargs.update({'header': None, # no effect...
                       'names': settings.BULK_BASE_NAMES})
        # !!! it seems there is a problem with compression='infer' since it is 
        # not working well !!!
        dcomp = {'gz': 'gzip', 'bz2': 'bz2', 'zip': 'zip'}
        #compression =[dcomp[ext] for ext in dcomp if settings.BULK_BASE_EXT.endswith(ext)][0]
        kwargs.update({'compression': dcomp[settings.BULK_BASE_ZIP]})
        # run the pandas.read_table method
        try:
            metabase = self.session.read_url_table(url, **kwargs)
        except:
            metabase = None
        return metabase

    #/************************************************************************/
    def search(self, regex):
        mask = np.column_stack([self.metabase[col].str.contains(regex, na=False) \
                                for col in self.metadata])
        res = self.metabase.loc[mask.any(axis=1)]
        return res
        
    #/************************************************************************/
    def setTOC(self, **kwargs):
        self.__toc = self.readToc(**kwargs)
    def readToc(self, **kwargs):
        """
        Example: http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=table_of_contents.xml
        """
        try:
            ext = kwargs.pop('ext')
        except:
            ext = settings.BULK_TOC_EXTS[0]
        else:
            if ext not in settings.BULK_TOC_EXTS:   
                raise pyroError('bulk table of contents extension EXT not recognised') 
        try:
            lang = kwargs.pop('lang')
        except:
            lang = self.lang
        else:
            if lang not in settings.LANGS:   
                raise pyroError('language LANG not recognised') 
        if ext == 'xml':
            tocfile = '{toc}.xml'.format(toc=settings.BULK_TOC_FILE)
        else:
            tocfile = '{toc}_{lang}.{ext}'.format(toc=settings.BULK_TOC_FILE, lang=lang, ext=ext)
        if settings.BULK_TOC_ZIP != '':
            tocfile = '{toc}.{zip}'.format(toc=tocfile, zip=settings.BULK_DIC_ZIP)
        url = self.update_url(self.url, sort=self.sort, file=tocfile)
        kwargs.update({'header': 0})
        try:
            if ext == 'xml':
                toc = self.session.read_html_table(url, **kwargs)                
                toc = toc[0]
            else:
                toc = self.session.read_url_table(url, **kwargs)
        except:
            toc = None
        else:
            toc.drop(toc.columns[-1], axis=1, inplace=True) # toc.columns[-1] is 'values'
            toc.applymap(lambda x: x.strip())
        return toc
         
    #/************************************************************************/
    @staticmethod
    def __get_content(member, toc, **kwargs):
        if toc is None:
            raise pyroError('table of contents not found - load the file from Eurobase')
        code = toc['code']
        if code[code.isin([member])].empty:
            raise pyroError('member not found in codelist of table of contents')
        return toc[code==member]
        
    #/************************************************************************/
    def getTitle(self, dataset, **kwargs):
        res = self.__get_content(dataset, self.toc, **kwargs)
        ind = res.index.tolist()
        return res['title'][ind[0]].lstrip().rstrip()
        
    #/************************************************************************/
    def getPeriod(self, dataset, **kwargs):
        res = self.__get_content(dataset, self.toc, **kwargs)
        ind = res.index.tolist()
        start = res['data start'][ind[0]]
        end = res['data end'][ind[0]]
        return [start, end]
    

class Rest(__Base):
    pass