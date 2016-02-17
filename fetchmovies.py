from bs4 import BeautifulSoup
from urllib2 import urlopen, HTTPError, URLError
from urlparse import urlparse, urljoin
import os.path

# Crawl a Thredds server and generate a list of all movie files

def domainof(url):
  parts = urlparse(url)
  domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parts)
  return domain

def moviecrawl(url):
  # Walk a Thredds directory and generate a list of all .mov and .mp4 files
  domain = domainof(url)
  response = urlopen(url)
  soup = BeautifulSoup(response.read(), "html.parser") 

  # yield all movie urls on this page, if any
  for ds in soup.find_all("thredds:dataset"):
    movurl = domain + ds[u'id']
    if "mov" in movurl:
        yield movurl
    if "mp4" in movurl:
        yield movurl

  for ds in soup.find_all("thredds:dataset"):
    base = ds[u'id']
    for c in ds.find_all("thredds:catalogref"):
      newurl = urljoin(urljoin(domain,base), c[u'xlink:href'])
      for movieurl in moviecrawl(newurl):
        yield movieurl
    
def download(url, localroot="."):
    # Open the url
    parts = urlparse(url)
    file_name = parts.path

    # Open our local file for writing
    path, basefile = os.path.split(file_name)
    localfiledir = os.path.join(localroot,path)
    os.makedirs(localfiledir)
    local_file_name = os.path.join(localfiledir, basefile)

    try:
        print "downloading " + url
        response = urlopen(url)

        CHUNK = 16 * 1024
        with open(local_file_name, 'wb') as f:
          while True:
            chunk = response.read(CHUNK)
            if not chunk: break
            f.write(chunk)
          f.close()

        return local_file_name
    #handle errors
    except HTTPError, e:
        print "HTTP Error:",e.code , url
    except URLError, e:
        print "URL Error:",e.reason , url


if __name__ == '__main__': 
  url = "http://opendap-devel.ooi.rutgers.edu:8080/opendap/hyrax/large_format/catalog.xml"
  #url = "http://opendap-devel.ooi.rutgers.edu:8080/opendap/hyrax/large_format/RS03ASHS-PN03B-06-CAMHDA301/2016/catalog.xml"

  for movieurl in moviecrawl(url):
    print movieurl
    # download(movieurl)
