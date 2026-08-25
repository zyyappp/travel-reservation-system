> **Create a complete draw.io flowchart based on the following programming logic. The flowchart must demonstrate all fundamental programming concepts for an introductory programming course.**
>
> ---
>
> ### Purpose
> Produce a clear, top-to-bottom flowchart that exemplifies the fundamental "Programming Concepts" taught in an introductory programming course. The diagram must include every core construct listed below and follow **strict visual conventions** derived from the reference style described here.
>
> ---
>
> ### CRITICAL STYLE RULES (must be obeyed without exception)
>
> 1. **NO COLORS.** Every shape must have a **black outline** and **white (or transparent) fill**. All text must be **black**. Do not use any colored fills, borders, gradients, or highlights anywhere in the diagram.
> 2. **Decision branch labels must be `True` and `False`** — never use `Yes`, `No`, `Y`, `N`, or any other variant.
> 3. **`True` exits the LEFT side** of every binary decision diamond. **`False` exits the RIGHT side.**
> 4. **Start and End shapes are OVALS (ellipses)** — not rounded rectangles, not stadium shapes. Use the draw.io ellipse shape.
> 5. **Branch merge points** (where True/False paths rejoin) must use a **small circle connector**, not a direct junction of lines.
> 6. **Input shapes** must be prefixed with the keyword `INPUT` (e.g., `INPUT savings`).
> 7. **Output shapes** must be prefixed with the keyword `PRINT` (e.g., `PRINT dividend`).
> 8. **`return` statements** are shown as a **process rectangle** containing the word `return`.
>
> ---
>
> ### Flowchart Symbol Conventions
>
> | draw.io Shape | Usage | draw.io Style Key |
> |---|---|---|
> | **Ellipse** (oval) | Start / End | `ellipse` |
> | **Rectangle** | Process, assignment, calculation, variable initialization, `return`, `for` loop header | `rounded=0` rectangle |
> | **Parallelogram** | Input (`INPUT …`) and Output (`PRINT …`) | Use draw.io's parallelogram or manually skewed shape |
> | **Diamond** (rhombus) | Decision / condition (`if`, `while` condition, menu choice) | `rhombus` |
> | **Pre-defined Process** (rectangle with double vertical bars on sides) | Function call / sub-process | `shape=process` |
> | **Small Circle** | On-page connector / branch merge point | Small `ellipse` (≈ 20×20 px) |
> | **Pentagon** (home-plate / arrow shape) | Off-page connector with label (e.g., `L1`, `L2`) | `shape=offPageConnector` |
> | **Arrow** (directed connector) | Flow direction between shapes | Standard connector |
>
> ---
>
> ### Program Logic to Represent
>
> Build the flowchart to represent this complete generic program:
>
> #### 1. Program Start
> - Oval shape containing the text `START`.
>
> #### 2. Variable Initialization
> - Process rectangle: `counter = 0`
> - Process rectangle: `valid = False`
>
> #### 3. Input Validation Loop (`while` style)
> - Parallelogram: `INPUT value`
> - Decision diamond: `value >= 0`
>   - **True** (left) → Process rectangle: `valid = True` → proceed to Main Menu
>   - **False** (right) → Parallelogram: `PRINT "Invalid input"` → small circle connector → loop back to `INPUT value`
>
> #### 4. Main Menu
> - Decision diamond: `choice == ?` with **three labeled outgoing branches**: `1`, `2`, `3`
>   - A fourth branch for **invalid choice** routes to error handling (see step 6).
>
> #### 5a. Branch 1 — Calculate (demonstrates `for` loop)
> - Process rectangle: `result = 0`
> - Process rectangle: `for i in range(N)` ← this is the loop header, represented as a single process rectangle
> - Inside loop body:
>   - Process rectangle: `result = result + f(i)`
>   - Decision diamond (nested condition): `result > THRESHOLD`
>     - **True** (left) → Process rectangle: `result = THRESHOLD` (cap the value)
>     - **False** (right) → small circle connector (skip, continue loop)
>     - Both branches merge at a small circle connector
> - Loop-back arrow from end of body back to the `for i in range(N)` process rectangle
> - After loop exits → Parallelogram: `PRINT result`
> - Arrow → small circle connector → back to Main Menu
>
> #### 5b. Branch 2 — Display (demonstrates simple output)
> - Parallelogram: `PRINT "Current results:"` 
> - Parallelogram: `PRINT counter, result`
> - Arrow → small circle connector → back to Main Menu
>
> #### 5c. Branch 3 — Exit
> - Direct arrow to the End oval.
>
> #### 6. Error Handling (invalid menu choice)
> - Parallelogram: `PRINT "Invalid choice"`
> - Arrow → small circle connector → back to Main Menu decision
>
> #### 7. Function / Sub-process (demonstrates pre-defined process)
> - The `f(i)` used inside the Calculate loop should be represented as a **pre-defined process** shape (rectangle with double vertical bars) labeled `f(i)`.
> - Show the function as a separate sub-flowchart nearby or below the main flow:
>   - Oval: `START f(i)`
>   - Process rectangle: `result = i * 2 + 1`
>   - Process rectangle: `return result`
>   - Oval: `END f(i)`
>
> #### 8. Program End
> - Oval shape containing the text `END`.
>
> ---
>
> ### Mapping Summary
>
> | Programming Construct | Flowchart Symbol | Branch Labels |
> |---|---|---|
> | Start / End | **Oval (ellipse)** | — |
> | Variable declaration / init | **Process (rectangle)** | — |
> | Assignment / calculation | **Process (rectangle)** | — |
> | User input | **Parallelogram** (`INPUT …`) | — |
> | Display output | **Parallelogram** (`PRINT …`) | — |
> | `if` / `else if` / `else` | **Decision (diamond)** | **`True`** (left) / **`False`** (right) |
> | `while` loop condition | **Decision (diamond)** + loop-back arrow | **`True`** (left) / **`False`** (right) |
> | `for` loop | **Process (rectangle)** for header + loop-back arrow | — |
> | Function call | **Pre-defined Process** (double-bar rectangle) | — |
> | `return` | **Process (rectangle)** containing `return` | — |
> | Branch merge | **Small circle connector** | — |
> | Off-page link | **Pentagon** with label | — |
> | Menu selection | **Decision (diamond)** | Numbered branches (`1`, `2`, `3`) |
> | Error handling | **Decision (diamond)** → error `PRINT` | **`True`** / **`False`** |
>
> ---
>
> ### Layout Requirements
>
> - **Primary flow**: top-to-bottom. Menu branches may fan out horizontally but must reconnect before the final `END`.
> - **Consistent vertical spacing** (≈ 30 pt) between successive shapes.
> - **Horizontal alignment**: parallel decision branches (True left, False right) must be horizontally aligned.
> - **Group related logic**: initialization block at top → validation loop → menu → branches.
> - **Minimize line crossings** by using connectors and routing arrows around blocks.
> - **Text inside shapes** must be short (≤ ~35 characters). Use multi-line text if needed.
> - **Connector labels** (`True`, `False`, `1`, `2`, `3`) placed close to the arrow source.
> - **Loop structures** must form a compact shape with a clear back-arrow.
> - **All shapes**: black outline, white fill, black text. **No colors whatsoever.**
>
> ---
>
> ### Assumptions
>
> - The program is single-threaded, console-based, and does not involve file I/O or external APIs.
> - All variables are of primitive types (integers, booleans, strings).
> - The menu offers exactly three valid choices plus error handling for invalid input.
> - `True` always exits the left side of a decision diamond; `False` always exits the right side.
>
> ---
>
> ### Validation Checklist (verify the finished diagram against this list)
>
> 1. ✅ Every construct in the Program Logic section appears at least once.
> 2. ✅ All decision diamonds have branches labeled **`True`** and **`False`** (never `Yes`/`No`).
> 3. ✅ `True` exits **left**, `False` exits **right** on every binary decision.
> 4. ✅ Menu decisions use numbered labels (`1`, `2`, `3`).
> 5. ✅ Start and End use **oval/ellipse** shapes.
> 6. ✅ Branch merge points use **small circle connectors**.
> 7. ✅ `for` loops use a process rectangle header + loop-back arrow.
> 8. ✅ `while` loops use a decision diamond + loop-back arrow.
> 9. ✅ At least one nested decision exists inside a loop.
> 10. ✅ At least one pre-defined process (function call) shape exists.
> 11. ✅ Input shapes are prefixed with `INPUT`, output shapes with `PRINT`.
> 12. ✅ **No colors** — all shapes are black outline, white/transparent fill, black text only.
> 13. ✅ No arrow leads to a dead-end; every path ends at `END` or loops back.
> 14. ✅ No shape contains overly long text (> ~35 characters).
> 15. ✅ Layout is top-to-bottom with minimal line crossings.
>
> **Deliver the flowchart in draw.io format** (XML / `.drawio` file) that can be opened directly in the draw.io editor. Ensure all shapes, connectors, and labels conform strictly to the conventions above.