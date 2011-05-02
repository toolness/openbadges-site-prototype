var fs = require('fs'),
    util = require('util'),
    url = require('url');

var config = null;

const STATIC_FILES_DIR = __dirname + '/static',
      TEMPLATE_FILE = __dirname + '/template.html';

const MIME_TYPES = {
  js: 'application/javascript',
  html: 'text/html',
  css: 'text/css'
};

function serveStaticFile(path, headers, return404, res) {
  var staticFilePath = STATIC_FILES_DIR + path;

  if (staticFilePath.match(/\/$/))
    staticFilePath += 'index.html';

  fs.realpath(staticFilePath, function(err, resolvedPath) {
    if (!err && resolvedPath.indexOf(STATIC_FILES_DIR + '/') == 0) {
      var extMatch = resolvedPath.match(/\.([a-z]+)$/);
      var mimetype;

      if (extMatch && extMatch[1] in MIME_TYPES) {
        mimetype = MIME_TYPES[extMatch[1]];

        fs.stat(resolvedPath, function(err, stats) {
          if (!err && stats.isFile()) {
            if (headers['if-none-match'] == stats.mtime) {
              res.writeHead(304);
              res.end();
            } else {
              res.writeHead(200, {
                'Content-Length': stats.size,
                'Content-Type': mimetype,
                'ETag': stats.mtime
              });
              var out = fs.createReadStream(resolvedPath);
              out.pipe(res);
            }
          } else
            return404();
        });
      } else
        return404();
    } else
      return404();
  });
}

function serveTemplatedFile(contentInfo, path, return404, res) {
  fs.readFile(TEMPLATE_FILE, 'utf8', function(err, data) {
    if (err) {
      util.log("Reading template file failed: " + TEMPLATE_FILE);
      res.writeHead(500);
      req.end();
    } else {
      var title = contentInfo.pathname.slice(1) + path;
      var protocol = require(contentInfo.protocol.slice(0, -1));
      var wikiReq = protocol.get({
        host: contentInfo.host,
        path: '/index.php?title=' + title + '&action=render'
      }, function(wikiRes) {
        var chunks = [];
        
        switch (wikiRes.statusCode) {
          case 404:
          return404();
          break;
          
          case 200:
          wikiRes.setEncoding('utf8');
          wikiRes.on('data', function(chunk) {
            chunks.push(chunk);
          });
          wikiRes.on('end', function() {
            var content = chunks.join('');
            var rendering = data.replace("{{ title }}", path)
                                .replace("{{ content }}", content)
                                .replace("{{ config }}",
                                         JSON.stringify(config));

            res.writeHead(200, {'Content-Type': 'text/html'});
            res.end(rendering);
          });
          break;
          
          default:
          res.writeHead(wikiRes.statusCode);
          res.end();
        }
      });
    }
  });
}

function serveRequest(req, res) {
  var path = url.parse(req.url).pathname;
  var staticFileMatch = path.match(/\/static(\/.*)/);

  function return404() {
    res.writeHead(404, {'Content-Type': 'text/plain'});
    res.end('not found: ' + path);
  }

  if (staticFileMatch) {
    return serveStaticFile(staticFileMatch[1], req.headers,
                           return404, res);
  } else if (path.match(/\/images\/.*/)) {
    var redirect = config.baseContentInfo.protocol + '//' +
                   config.baseContentInfo.host + path;
    res.writeHead(302, {'Location': redirect});
    res.end();
  } else {
    return serveTemplatedFile(config.baseContentInfo, path,
                              return404, res);
  }
}

function loadConfig() {
  function loadJSONFile(filename) {
    var obj = null;
    try {
      return JSON.parse(fs.readFileSync(filename));
    } catch (e) {
      util.log("Error parsing " + filename + ": " + e);
      process.exit(1);
    }
  }

  var config = loadJSONFile('config.json');
  config.baseContentInfo = url.parse(config.baseContent);
  return config;
}

config = loadConfig();

server = require('http').createServer(serveRequest);

server.listen(config.port, config.hostname);

util.log("Now listening on port " + config.port);

process.on('uncaughtException', function(err) {
  util.log(err.stack);
  util.log(err.message);    
});
