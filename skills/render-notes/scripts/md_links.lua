-- Rewrite relative links to .md files so they point at the rendered .html instead.
-- Absolute URLs (anything with a scheme) are left alone.
function Link(el)
  if el.target:match("^%a[%w+.-]*:") then
    return el
  end
  local path, anchor = el.target:match("^(.-)%.md(#.*)$")
  if path then
    el.target = path .. ".html" .. anchor
  elseif el.target:match("%.md$") then
    el.target = el.target:gsub("%.md$", ".html")
  end
  return el
end
