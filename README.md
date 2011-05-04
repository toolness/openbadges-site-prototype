# Introduction And Motivation

This is a prototype for the [openbadges.org][] site.

Most [Mozilla Drumbeat][] projects start off as wiki pages and evolve into websites once they get off the ground. However, turning them into scalable, production-ready websites takes a lot of time and it's often the case that there are barriers to making simple modifications to them.

The goal of this prototype is to explore the possibility of a "middle ground" between a wiki and a website, for situations when a wiki no longer fully suits a project's needs, but the project also doesn't have the resources or demand to host a full-blown website.

This simple prototype uses a project's existing wiki as a "back end" for a website. A very simple templating mechanism makes it easy for project participants to give the website its own look, feel, and functionality using HTML, CSS, and JavaScript, while the site's core content is drawn from existing wiki pages. This allows a project to extend and evolve its web presence into something that better serves the needs of a more diverse community.

# URL Mapping

The site mirrors content at [https://wiki.mozilla.org/Badges][wiki], and hosts anything that starts with it. Thus, for instance, this page: 

    https://wiki.mozilla.org/Badges/Backpack

Can be viewed at:

    http://openbadges.org/Backpack

All other wiki links remain unmodified and point back to the original site.

The only exception here is the `/static/` directory, which maps directly to files in the [static][] directory of this repository. These files are generally only referenced by the template.

# Templating

The file [template.html][] is used as a simple template every page on the site. The following strings are dynamically replaced by the server:

* `{{ title }}` is the title of the page. Currently, this is just the path part of the URL, but it should probably be changed to something more user-friendly.

* `{{ content }}` is the raw HTML-rendered content of the wiki page being viewed, not including any header/footer/sidebar content.

* `{{ config }}` is a JSON blob containing some configuration information useful to client-side JavaScript.

# Editing Files

If you're a designer, ask [Atul][] for commit access to this repository. Once you have it, you can edit the template file and any static files by visiting them on github and clicking the "Edit this file" button. As soon as you commit your changes, the openbadges.org site is automatically updated.

Alternatively, you're also welcome to [fork with the edit button][fork].

# Running The Server

The core server requires [node.js][] and has been tested with v0.3.6.

To start the server, run this in your shell:

    $ git clone git://github.com/toolness/openbadges-site-prototype.git
    $ cd openbadges-site-prototype
    $ node server.js

Then, open http://localhost:8072 in your browser.

<!-- Links begin here. -->

  [Atul]: https://github.com/toolness
  [node.js]: http://nodejs.org/
  [Mozilla Drumbeat]: http://drumbeat.org/
  [openbadges.org]: http://openbadges.org/
  [wiki]: https://wiki.mozilla.org/Badges
  [template.html]: https://github.com/toolness/openbadges-site-prototype/blob/master/template.html
  [static]: https://github.com/toolness/openbadges-site-prototype/tree/master/static
  [fork]: https://github.com/blog/844-forking-with-the-edit-button
