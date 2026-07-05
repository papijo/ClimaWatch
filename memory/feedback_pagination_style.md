---
name: feedback_pagination_style
description: User prefers page/limit pagination with adjustable row count for admin tables, not cursor-based
metadata:
  type: feedback
---

Use page/limit (offset-based) pagination for all admin panel tables, not cursor-based.

**Why:** User explicitly requested page number navigation and an adjustable rows-per-page control. Cursor-based pagination does not support jumping to arbitrary pages or showing a row count selector.

**How to apply:** For any new admin list endpoint or table, implement `page` (1-indexed) + `limit` query params on the backend, and a full pagination UI (rows-per-page select + page number buttons) on the frontend. Default limit = 10. The CLAUDE.md cursor-based rule applies to public API endpoints only — admin panel tables are exempt per user instruction.
</content>
</invoke>