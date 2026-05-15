<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9">
<xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
<xsl:template match="/">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Macro &amp; Meals — Sitemap</title>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <style>
    body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:0;padding:2rem;background:#f8fafc;color:#1e293b}
    h1{color:#22c55e;margin-bottom:.25rem}
    p.info{color:#64748b;margin-bottom:1.5rem;font-size:.95rem}
    table{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.1)}
    th{background:#22c55e;color:#fff;padding:.75rem 1rem;text-align:left;font-weight:600;font-size:.85rem;text-transform:uppercase;letter-spacing:.05em}
    td{padding:.6rem 1rem;border-bottom:1px solid #e2e8f0;font-size:.9rem}
    tr:hover td{background:#f0fdf4}
    a{color:#22c55e;text-decoration:none}
    a:hover{text-decoration:underline}
    .priority{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.8rem;font-weight:600}
    .p10{background:#dcfce7;color:#166534}.p09{background:#d1fae5;color:#065f46}.p08{background:#e0f2fe;color:#075985}
    .p07{background:#fef3c7;color:#92400e}.p06{background:#f1f5f9;color:#475569}.p05{background:#f1f5f9;color:#64748b}
    #count{color:#64748b;font-size:.85rem;margin-top:1rem}
  </style>
</head>
<body>
  <h1>Macro &amp; Meals — XML Sitemap</h1>
  <p class="info">This sitemap contains <xsl:value-of select="count(sitemap:urlset/sitemap:url)"/> URLs for search engine crawlers.</p>
  <table>
    <tr><th>#</th><th>URL</th><th>Priority</th><th>Change Freq</th><th>Last Modified</th></tr>
    <xsl:for-each select="sitemap:urlset/sitemap:url">
      <tr>
        <td><xsl:value-of select="position()"/></td>
        <td><a href="{sitemap:loc}"><xsl:value-of select="sitemap:loc"/></a></td>
        <td>
          <xsl:variable name="p" select="sitemap:priority"/>
          <span>
            <xsl:attribute name="class">priority <xsl:choose>
              <xsl:when test="$p='1.0'">p10</xsl:when>
              <xsl:when test="$p='0.9'">p09</xsl:when>
              <xsl:when test="$p='0.8'">p08</xsl:when>
              <xsl:when test="$p='0.7'">p07</xsl:when>
              <xsl:when test="$p='0.6'">p06</xsl:when>
              <xsl:otherwise>p05</xsl:otherwise>
            </xsl:choose></xsl:attribute>
            <xsl:value-of select="sitemap:priority"/>
          </span>
        </td>
        <td><xsl:value-of select="sitemap:changefreq"/></td>
        <td><xsl:value-of select="substring(sitemap:lastmod,1,10)"/></td>
      </tr>
    </xsl:for-each>
  </table>
  <p id="count">Total: <xsl:value-of select="count(sitemap:urlset/sitemap:url)"/> URLs</p>
</body>
</html>
</xsl:template>
</xsl:stylesheet>