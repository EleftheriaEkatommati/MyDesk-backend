# Frontend Update Notification

## Backend Changes Summary

We've updated the database schema and API to properly normalize floor data. Desks now reference floors via ID instead of storing floor names as strings.

### New API Endpoints
- `GET /api/desks/floors` — Returns list of all floors with metadata:
  ```json
  [
    {
      "id": 1,
      "floorNumber": 1,
      "floorName": "1st Floor"
    }
  ]
  ```

### Updated Desk API Responses
All desk-related endpoints now include floor information:
- `GET /api/desks` 
- `GET /api/desks/floor/{floor_name}`
- `POST /api/desks/{desk_id}/book`

New fields in desk responses:
- `floorId`: integer (foreign key to floors.id)
- `floorName`: string (floor name, nullable)
- `floor`: string (kept for backward compatibility, same as floorName)

Example desk response:
```json
{
  "id": "101",
  "x": 60.0,
  "y": 80.0,
  "rotation": 180,
  "floorId": 1,
  "floorName": "1st Floor",
  "floor": "1st Floor",
  "isBooked": false,
  "bookedBy": null
}
```

### Frontend Migration Steps
1. **Fetch floors data**: Use `GET /api/desks/floors` to get available floors
2. **Update desk rendering**: Use `floorId` or `floorName` for floor identification instead of the old `floor` string
3. **Floor filtering**: Update any floor-based filtering to use floor IDs or names from the floors endpoint
4. **Backward compatibility**: The `floor` field is still included, but prefer `floorName` for new code

### Breaking Changes
- If your frontend was parsing floor data from desk objects, update to use the new structure
- Floor names are now centralized in the floors table — use the `/floors` endpoint for floor lists

Contact backend team if you need the full Floor schema or have questions about the data migration.