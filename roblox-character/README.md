# Neon Ranger: Roblox character from the reference art

A blue-haired cat-girl archer in a neon "Robin Hood" style, adapted to Roblox's classic blocky style.

## Files

| File | What it is | Where it goes |
|---|---|---|
| `upload/NeonRanger_Shirt_585x559.png` | **Classic Shirt template** (torso + arms) | Upload as a *Shirt* |
| `upload/NeonRanger_Pants_585x559.png` | **Classic Pants template** (legs + matching torso) | Upload as *Pants* |
| `upload/NeonRanger_Face_512.png` | Face decal (transparent PNG) | Roblox Studio only (see below) |
| `preview/NeonRanger_Front.png` | Front view | Reference |
| `preview/NeonRanger_Back.png` | Back view | Reference |
| `preview/NeonRanger_Character_Sheet.png` | Front + back + templates + palette + accessory list on one page | Reference |
| `sandbox/index.html` | Interactive 3D preview (Three.js) of the Shirt/Pants/Face on an R6 block rig. Open it at https://claude.ai/artifact/N6k6XfePEVUHh1JzG8jBPw | Phone browser |
| `studio/BuildNeonRanger.lua` | One-paste Studio script that dresses a rig and builds the hat, ears, hair, halo and bow from parts | Roblox Studio (Mac/PC) |
| `NeonRanger_Roblox_Assets.zip` | Everything above in one download | Save to the Files app |
| `source/generate.py` | Regenerates all the images | — |

Both templates use the standard 585×559 Roblox layout, with every panel in its official position. Transparent pixels fall outside the panels.

## What was kept from the reference

- **Hair:** electric-blue bob with bangs, side locks and violet rim light
- **Cat ears:** blue-violet with pink insides and white fluff
- **Hat:** dark-green Robin Hood cap with gold trim, a green-star badge and a magenta feather
- **Halo:** neon magenta
- **Face:** big sparkly violet eyes, purple forehead gem, black visor strap with gold fittings, blue lips with the tongue peeking out, blush
- **Cloak:** dark-green hood and cloak with gold trim, the leaf-shaped hem and green-star gold brooches
- **Corset:** laced green corset, gold chain with a green gem
- **Straps and gloves:** brown leather straps and belt, black gloves with leather bracers
- **Bow:** dark bow with neon-green arrow glyphs and a glowing magenta string
- **Quiver:** brown quiver with a green-star emblem and green-fletched arrows, painted on the back of the shirt

**Extrapolated:** the reference is cropped at the waist, so the black leggings, brown boots and the cloak hem behind the legs are my guess. I built them only from colours and materials already in the image. Nothing else is invented.

## Part 1: Put the clothing on your avatar (all on iPhone)

1. **Save the files.** Tap each PNG in `upload/` → Share → **Save to Files**. Files keeps the exact PNG. Saving to Photos can convert it to JPEG, which loses transparency.
2. Open **Safari** → go to **create.roblox.com** → sign in.
   - If a page says it needs a computer, tap **aA** in the address bar → **Request Desktop Website**.
3. Go to **Creations** → **Avatar Items** → **Upload Asset**. (Roblox sometimes renames these menus. Look for "Avatar Items" or "Upload".)
4. Choose **Shirt** → **Choose File** → *Browse* → pick `NeonRanger_Shirt_585x559.png` → name it *Neon Ranger Shirt* → upload.
   Classic clothing has a small **Robux upload fee** (Roblox has charged 10 Robux). The upload screen shows the current price before you pay.
5. Repeat with **Pants** → `NeonRanger_Pants_585x559.png`.
6. Wait for moderation to approve the items. This is usually minutes, sometimes hours.
7. In the **Roblox app** → **Avatar** → **Clothing** → **Shirts / Pants**, wear both.
8. Finish the look in the Avatar editor:
   - **Body:** a blocky / classic body gives the cleanest fit for classic clothing.
   - **Skin tone:** a pale pink-lilac (`#F4E2EE`).
   - **Accessories:** search the Marketplace for close matches: *blue bob hair*, *cat ears* (blue or purple), *robin hood hat* / *green feather hat*, *pink neon halo*, *bow* / *archer bow*, *quiver*.
   - **Face:** search *purple anime eyes* or *sparkle eyes*. Roblox doesn't let you upload a custom avatar face (see below).

## Part 2: What can't be finished on an iPhone

- **Custom face on your avatar:** Roblox doesn't allow uploading classic face images as avatar items. Faces are now 3D heads made in Blender and sold through the UGC program. You can still use `NeonRanger_Face_512.png` on characters **inside your own game** in Studio.
- **Hair, cat ears, hat, halo, bow as your own avatar items:** these are 3D accessories. They need a 3D model (Blender), fitting in **Roblox Studio on a Mac or PC**, and UGC upload access. The character sheet gives the design, colours and hex codes so a 3D artist, or you later, can build them.
- **The final step in Roblox Studio (for an in-game character or NPC):**
  1. Studio → **Avatar** tab → **Rig Builder** → *Block Rig*.
  2. Import the three PNGs (**Asset Manager** → *Import*). Right-click each one → *Copy Asset ID*.
  3. Paste those IDs into the top of `studio/BuildNeonRanger.lua`.
  4. Select the rig, paste the whole script into **View → Command Bar**, press Enter.
     This adds the shirt, pants, face and skin colour, plus part-built versions of the hair, cat ears, Robin Hood cap, feather, glowing halo and neon bow.

The Studio route doesn't need the Marketplace upload fee. Uploading images for your own game is free.

## Regenerating

```
pip install pillow numpy
python3 source/generate.py
```
