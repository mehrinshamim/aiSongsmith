Here’s the **tabular view** of your updated models, followed by a comparison with the previous version.

---

## **Updated Models in `backend/songsmith/models.py`**  

### **1. Profile Model**
| Field Name             | Data Type         | Attributes               | Description |
|------------------------|------------------|--------------------------|-------------|
| `user_id`             | UUIDField         | `primary_key=True, default=uuid.uuid4, editable=False` | Unique identifier for each profile |
| `user`                | OneToOneField (User) | `CASCADE`                | Links to Django’s built-in User model |
| `first_name`          | CharField(100)    | -                        | Stores user's first name |
| `last_name`           | CharField(100)    | -                        | Stores user's last name |
| `spotify_refresh_token` | TextField        | `null=True`              | Stores Spotify refresh token |
| `spotify_access_token` | TextField        | `null=True`              | Stores Spotify access token |
| `token_expires_at`    | DateTimeField     | `null=True`              | Stores token expiration time |
| `created_at`          | DateTimeField     | `auto_now_add=True`      | Timestamp when the profile was created |
| `updated_at`          | DateTimeField     | `auto_now=True`          | Timestamp when the profile was last updated |

---

### **2. ListeningContext Model**
| Field Name    | Data Type         | Attributes               | Description |
|--------------|------------------|--------------------------|-------------|
| `context_id` | UUIDField         | `primary_key=True, default=uuid.uuid4, editable=False` | Unique identifier for each context |
| `user`       | ForeignKey (Profile) | `CASCADE`                | Links to the user profile |
| `context`    | CharField(50)     | -                        | Stores the type of context (e.g., "happy", "workout") |
| `created_at` | DateTimeField     | `auto_now_add=True`      | Timestamp when the context was created |

---

### **3. SongDetail Model**
| Field Name      | Data Type    | Attributes               | Description |
|----------------|-------------|--------------------------|-------------|
| `song_id`      | CharField(100) | `primary_key=True`      | Stores the unique Spotify track ID |
| `name`         | CharField(200) | -                        | Song title |
| `artists`      | JSONField     | -                        | List of artists stored in JSON format |
| `lyrics`       | TextField     | `null=True`              | Stores song lyrics |
| `lyrics_last_updated` | DateTimeField | `null=True`     | Timestamp when lyrics were last updated |

---

### **4. PlayHistory Model**
| Field Name     | Data Type         | Attributes               | Description |
|---------------|------------------|--------------------------|-------------|
| `history_id`  | UUIDField         | `primary_key=True, default=uuid.uuid4, editable=False` | Unique identifier for each play history record |
| `context`     | ForeignKey (ListeningContext) | `CASCADE`      | Links to the listening context |
| `song`        | ForeignKey (SongDetail) | `CASCADE`      | Links to the played song |
| `liked`       | BooleanField      | `null=True`              | Indicates if the user liked the song |
| `order_in_list` | IntegerField    | -                        | Order in which the song was played within a session |
| `played_at`   | DateTimeField     | `auto_now_add=True`      | Timestamp when the song was played |

---

## **Comparison with Previous Models**
| Feature                 | Old Models                         | Updated Models                          | Changes/Improvements |
|-------------------------|----------------------------------|----------------------------------------|----------------------|
| **Profile Model**        | Used `id` (AutoField) as primary key | Uses `user_id` (UUIDField) as primary key | More unique & secure IDs |
|                         | Stored `spotify_refresh_token` only | Added `spotify_access_token` & `token_expires_at` | Better Spotify API integration |
|                         | No first/last name fields       | Added `first_name` & `last_name`       | More user data stored |
| **ListeningContext**     | Used `id` (UUIDField) as primary key | Renamed to `context_id` (UUIDField)    | Consistent naming convention |
|                         | ForeignKey linked to `User`     | ForeignKey linked to `Profile`         | Improved relational integrity |
|                         | `context_type` and `context_value` | Merged into `context` field | Simplified storage |
| **Song Model**          | Did not exist                    | `SongDetail` model added                | Stores song metadata, lyrics, and artists |
| **PlayHistory Model**    | Used `song_id` as CharField    | Uses ForeignKey to `SongDetail`        | Normalized database structure |
|                         | No explicit `order_in_list` field | Added `order_in_list`                  | Maintains order of songs played |

---

### **Key Takeaways from the Changes**
✅ **Better Database Design**: The new models provide **stronger normalization** (separating songs into `SongDetail`) and **more structured relationships**.  
✅ **Improved Spotify Integration**: The new `Profile` model includes both **refresh and access tokens**.  
✅ **More Meaningful Identifiers**: Using `UUIDField` as the primary key improves **security** and **uniqueness**.  
✅ **More Efficient Data Storage**: Instead of duplicating song details in every play history entry, **PlayHistory** now references `SongDetail`.  

