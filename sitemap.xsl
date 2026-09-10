<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html lang="en">
      <head>
        <title>Sitemap - redageddon.com</title>
        <meta charset="UTF-8"/>
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0d0f14;
            color: #e6e6e6;
            margin: 0;
            padding: 2rem;
          }
          h1 {
            color: #00e5ff;
            font-size: 1.4rem;
            margin-bottom: 0.25rem;
          }
          p.sub {
            color: #888;
            margin-top: 0;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            background: #12141c;
            border: 1px solid #23262f;
          }
          th {
            text-align: left;
            background: #181b24;
            color: #00e5ff;
            padding: 0.6rem 0.9rem;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            border-bottom: 1px solid #23262f;
          }
          td {
            padding: 0.6rem 0.9rem;
            border-bottom: 1px solid #1c1f28;
            font-size: 0.9rem;
          }
          tr:hover td {
            background: #161923;
          }
          a {
            color: #ff2e88;
            text-decoration: none;
          }
          a:hover {
            text-decoration: underline;
          }
          .count {
            color: #888;
            font-size: 0.85rem;
            margin-top: 1rem;
          }
        </style>
      </head>
      <body>
        <h1>XML Sitemap</h1>
        <p class="sub">redageddon.com</p>
        <table>
          <tr>
            <th>URL</th>
            <th>Last Modified</th>
            <th>Change Frequency</th>
            <th>Priority</th>
          </tr>
          <xsl:for-each select="sitemap:urlset/sitemap:url">
            <tr>
              <td>
                <a href="{sitemap:loc}">
                  <xsl:value-of select="sitemap:loc"/>
                </a>
              </td>
              <td><xsl:value-of select="sitemap:lastmod"/></td>
              <td><xsl:value-of select="sitemap:changefreq"/></td>
              <td><xsl:value-of select="sitemap:priority"/></td>
            </tr>
          </xsl:for-each>
        </table>
        <p class="count">
          <xsl:value-of select="count(sitemap:urlset/sitemap:url)"/> URL(s)
        </p>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
