import httplib, urllib, sys, webbrowser
import json

def getJSONForRequest(string):
    RTConn = httplib.HTTPConnection('api.rottentomatoes.com')
    qDict = {'apikey':'w4gcye5tysdwhngptet3vgv2','q':string,'page_limit':4,'page':1}
    query = urllib.urlencode(qDict)
    RTConn.request("GET",'/api/public/v\
1.0/movies.json?%s'%(query))
    res = RTConn.getresponse()
    print res.status, res.reason
    data = res.read()
    result = json.loads(data)
    for movie in result['movies']:
        if movie['title'] == string:
            return movie
    return result['movies'][0]

def prettyOutput(movie):
    print movie['title']
    print '\nreleased: %s'%(movie['release_dates']['theater'])
    print '\nscore: %s%% '%(movie['ratings']['critics_score'])
    if 'critics_rating' in movie['ratings']:
        print '- %s'%(movie['ratings']['critics_rating'])
    print '\nposter: %s'%(movie['posters']['detailed'])
    webbrowser.open(movie['posters']['detailed'])
    print '\nruntime: %s minutes'%(movie['runtime'])
    print '\nMPAA: %s'%(movie['mpaa_rating'])
    if len(movie['synopsis']) > 1:
        print '\n%s'%(movie['synopsis'])
    elif 'critics_consensus' in movie:
        print '\n%s'%(movie['critics_consensus'])

print sys.argv[1]
m =  getJSONForRequest(sys.argv[1])
if len(sys.argv) > 2:
    print m
prettyOutput(m)
