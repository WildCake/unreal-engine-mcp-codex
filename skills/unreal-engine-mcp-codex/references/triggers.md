# Trigger Reference

Use this reference when a task likely targets Unreal Engine even if the user does not say "Unreal" directly. Keep the frontmatter description short; broad aliases live here.

## Strong Project Signals

- `.uproject`, `.uplugin`, `.umap`, `.uasset`
- `DefaultEngine.ini`, `DefaultGame.ini`, `DefaultEditor.ini`
- `Source/<ProjectName>/<ProjectName>.Build.cs`
- `Plugins/<PluginName>/<PluginName>.uplugin`
- `Content/`, `Config/`, `Saved/`, `Intermediate/`, `Binaries/`, `DerivedDataCache/`

## C++ and Reflection Signals

- `UCLASS`, `USTRUCT`, `UENUM`, `UINTERFACE`
- `UPROPERTY`, `UFUNCTION`, `GENERATED_BODY`
- `UObject`, `AActor`, `UActorComponent`, `UGameInstance`, `UWorld`
- UHT, UBT, Live Coding, Hot Reload
- `Build.cs`, `Target.cs`, module rules, reflected schema, commandlet

## Asset and Naming Prefixes

- `BP_`, `BPI_`, `WBP_`, `ABP_`
- `M_`, `MI_`, `MF_`, `T_`, `RT_`
- `NS_`, `PS_`, `FX_`
- `SM_`, `SK_`, `S_`, `PHYS_`, `CTRL_`, `CR_`
- `DA_`, `DT_`, `EQS_`, `BT_`, `BB_`, `ST_`
- `L_`, `LV_`, `SEQ_`, `LS_`

## Editor and Workflow Signals

- Content Browser, Outliner, Details panel, World Settings
- PIE, Simulate, Standalone, viewport, PlayerStart
- Blueprint graph, Widget Blueprint, Material Editor
- Niagara, Sequencer, Control Rig, State Tree, Behavior Tree, GAS
- Data Validation, Automation Tests, Functional Tests
- Cook, package, staging, RunUAT, `UnrealEditor-Cmd.exe`

## Do Not Trigger

- Unity scenes, prefabs, packages, or C# scripts unless the user asks to port to Unreal.
- Godot scenes, `.tscn`, `.gd`, `.godot`, or GDScript unless the user asks for Unreal migration planning.
- General "blueprint" as a planning document or architecture sketch.
- Conceptual Unreal explanations that do not require project inspection, editor state, MCP tools, or command-line Unreal execution.
