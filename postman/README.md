# Postman Collection

## Import (do both)

1. Postman → **Import**
2. Import:
   - `Product_Inventory_API.postman_collection.json`
   - `Product_Inventory_Local.postman_environment.json`
3. **Required:** top-right dropdown → select **Product Inventory - Local**  
   If this says `No Environment`, tokens will **not** appear in the Environment panel (`pm.environment.set` needs an active env).

## Admin credentials (already in environment)

| Field | Value |
|-------|--------|
| username | `admin@yopmail.com` |
| password | `Welcome@123` |

Use **Auth → Login (Admin)**.

## Why tokens were not saving

1. **No environment selected** → `pm.environment.set()` does nothing.
2. Empty env `access_token` can override collection values → requests send no Bearer token.
3. Scripts only run on **200** responses — failed login won't save anything.

## Verify

1. Select environment **Product Inventory - Local**
2. Run **Login (Admin)**
3. Open **Console** (View → Show Postman Console) — you should see `access_token saved`
4. Environment → check `access_token` and `refresh_token` are filled
5. Collection variables are also updated as a backup

## Test order

1. **Auth → Login (Admin)**
2. **Categories → Create Category**
3. **Products → Create Product**
4. Search / filter / pagination under **Products**
5. **Auth → Login** (customer) — place orders need a non-admin user
6. **Orders → Place Order** — `order_id` auto-saves
7. **Orders → Order History** / Detail / Cancel
8. **Auth → Login (Admin)** → **Update Order Status**
9. **Refresh Token** / **Logout** as needed

## Included APIs

| Folder | Endpoints |
|--------|-----------|
| Auth | register, login, refresh, logout |
| Categories | list, create, detail, update, soft-delete |
| Products | list (+ search/filter/page/sort), create, detail, update, soft-delete |
| Orders | place, list, history, detail, update status, cancel |
| Docs | Swagger UI, OpenAPI schema |

## Not included yet

- Dashboard — not wired in root URLs yet
