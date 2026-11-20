# Character reference images

Visual anchors for the 3D models. Models are built from `bible/characters/*.json`;
these images inform face shape, complexion, beard, pagdi style and dress.

| File | Subject | Source |
|---|---|---|
| `gokulnathji_manuscript.jpg` | Gokulnathji reciting from a manuscript, c. 1840, gouache | theindianportrait.com/artwork/gokulnathji-reciting-from-a-manuscript |
| `vallabhacharya_reference.jpg` | Vallabhacharya | Wikimedia Commons |

## Notes

- These are devotional paintings, not photographs. Use them for costume and
  bearing, not as literal facial likenesses.
- Kalyanbhatt, the young Vaishnav and Damodardas have no reliable standalone
  portraits online. Their models come from the source text's descriptions
  (region, caste, age, dress) and from period Pushtimarg painting conventions.
- No reference image is used as a texture in the render. All models are
  procedural Three.js geometry locked by seed in `bible/characters/`.
- Wikimedia direct downloads were rate-limited on this machine; the two images
  above are what could be retrieved. Add more here when available.
