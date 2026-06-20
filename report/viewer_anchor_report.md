# Isomorph Viewer → anchor candidacy report

*Reproduce: `python3 eyewitness/viewer_anchor.py`. Classifies viewer patterns via `chain_extract` consensus GF.*

| rank | tier | pattern | L | inst | clean | score | refrain | notes |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | CERTIFIED | `ABC.DC.AD.B` | 11 | 4 | 6/6 | 20.2 | 4 | West 1@40, West 1@70, East 2@45, East 2@80 |
| 2 | CERTIFIED | `AB.CB..C.A` | 10 | 4 | 6/6 | 12.5 | 4 | West 1@41, West 1@71, East 2@46, East 2@81 |
| 3 | LIKELY | `A.....BCD.ED.BE.CA` | 18 | 4 | 6/6 | 28.0 | 4 | West 1@34, West 1@64, East 2@39, East 2@74 |
| 4 | LIKELY | `AB......A.C.D.BD.CB` | 19 | 3 | 3/3 | 20.8 | 2 | East 1@30, West 1@30, East 2@35 |
| 5 | LIKELY | `AB...C...C......D.A...E...EB.D` | 30 | 3 | 3/3 | 20.9 | 0 | East 4@68, West 4@71, East 5@69 |
| 6 | REFRAIN-ADJ | `AB..C...A.DEF.BF.DB.EC` | 22 | 2 | 1/1 | 21.3 | 2 | West 1@30, East 2@35 |
| 7 | LIKELY | `A........B.C.AC.BA` | 18 | 3 | 3/3 | 15.0 | 2 | East 1@31, West 1@31, East 2@36 |
| 8 | REFRAIN-ADJ | `A.....BCD.ED.BE.CA..F....F` | 26 | 2 | 1/1 | 17.5 | 2 | West 1@34, West 1@64 |
| 9 | LIKELY | `A...B...B......C.....D...DA.C` | 29 | 3 | 3/3 | 15.1 | 0 | East 4@69, West 4@72, East 5@70 |
| 10 | REFRAIN-ADJ | `A.....BCD.ED.BE.CAF....F` | 24 | 2 | 1/1 | 17.5 | 2 | East 2@39, East 2@74 |
| 11 | LIKELY | `AB...C...C........A...D...DB` | 28 | 3 | 3/3 | 15.1 | 0 | East 4@68, West 4@71, East 5@69 |
| 12 | REFRAIN-ADJ | `AB......A.CDE.BE.CB.D` | 21 | 2 | 1/1 | 17.5 | 2 | West 1@30, East 2@35 |
| 13 | REFRAIN-ADJ | `A..B.....CDE.AE.CA.DB` | 21 | 2 | 1/1 | 17.5 | 2 | West 1@31, East 2@36 |
| 14 | LIKELY | `A...A......B.....C...C..B` | 25 | 4 | 6/6 | 12.8 | 0 | East 3@64, East 4@73, West 4@76, East 5@74 |
| 15 | PARTIAL | `A.B.CB.AC` | 9 | 6 | 14/15 | 19.5 | 4 | East 1@40, East 1@68, West 1@40, West 1@70, +2 |
| 16 | LIKELY | `AB......A...C.BC` | 16 | 3 | 3/3 | 9.2 | 2 | East 1@30, West 1@30, East 2@35 |
| 17 | REFRAIN-ADJ | `A........BCD.AD.BA.C` | 20 | 2 | 1/1 | 13.6 | 2 | West 1@31, East 2@36 |
| 18 | REFRAIN-ADJ | `ABC.DC.AD.B...E....E` | 20 | 2 | 1/1 | 13.6 | 2 | West 1@40, West 1@70 |
| 19 | REFRAIN-ADJ | `ABC.DC.AD.B.E....E` | 18 | 2 | 1/1 | 13.6 | 2 | East 2@45, East 2@80 |
| 20 | LIKELY | `A....B...B........A...C...C` | 27 | 3 | 3/3 | 9.4 | 0 | East 4@68, West 4@71, East 5@69 |
| 21 | LIKELY | `A...B...B............C...CA` | 27 | 3 | 3/3 | 9.4 | 0 | East 4@69, West 4@72, East 5@70 |
| 22 | REFRAIN-ADJ | `AB.CB..C.A...D....D` | 19 | 2 | 1/1 | 9.8 | 2 | West 1@41, West 1@71 |
| 23 | REFRAIN-ADJ | `AB.CB..C.A.D....D` | 17 | 2 | 1/1 | 9.8 | 2 | East 2@46, East 2@81 |
| 24 | LIKELY | `AB.C....B.AC` | 12 | 3 | 3/3 | 9.1 | 0 | East 4@51, West 4@53, East 5@52 |
| 25 | LIKELY | `AB......A.....B` | 15 | 3 | 3/3 | 3.5 | 2 | East 1@30, West 1@30, East 2@35 |
| 26 | LIKELY | `A..........B.AB` | 15 | 3 | 3/3 | 3.5 | 2 | East 1@31, West 1@31, East 2@36 |
| 27 | LIKELY | `A...A............B...B` | 22 | 4 | 6/6 | 5.1 | 0 | East 3@64, East 4@73, West 4@76, East 5@74 |
| 28 | LIKELY | `A...B...B........A` | 18 | 4 | 6/6 | 5.0 | 0 | East 3@77, East 4@2, West 4@2, East 5@2 |
| 29 | LIKELY | `A.....B...B..A` | 14 | 4 | 6/6 | 4.9 | 0 | East 3@75, East 4@84, West 4@87, East 5@85 |
| 30 | REFRAIN-ADJ | `A.BA..B.....C....C` | 18 | 2 | 1/1 | 5.9 | 2 | West 1@42, West 1@72 |
| 31 | REFRAIN-ADJ | `A.BA..B...C....C` | 16 | 2 | 1/1 | 5.9 | 2 | East 2@47, East 2@82 |
| 32 | PARTIAL | `A.B..B.A` | 8 | 7 | 20/21 | 9.7 | 4 | East 1@40, East 1@68, West 1@40, West 1@70, +3 |
| 33 | LIKELY | `A..B.B.......A` | 14 | 3 | 3/3 | 3.5 | 0 | West 2@18, East 3@24, West 3@23 |
| 34 | LIKELY | `AB......B.A` | 11 | 3 | 3/3 | 3.4 | 0 | East 4@51, West 4@53, East 5@52 |
| 35 | LIKELY | `A.B....A..B` | 11 | 3 | 3/3 | 3.4 | 0 | East 4@52, West 4@54, East 5@53 |
| 36 | PARTIAL | `AB..C...C......D.....E...EA.DB` | 30 | 2 | 1/1 | 13.7 | 0 | East 4@69, West 4@72 |
| 37 | PARTIAL | `A..BA.........B..CD.E....D.CE` | 29 | 2 | 1/1 | 13.7 | 0 | West 4@36, East 5@35 |
| 38 | REFRAIN-ADJ | `A...A.....B....B` | 16 | 2 | 1/1 | 2.1 | 2 | West 1@44, West 1@74 |
| 39 | PARTIAL | `A.B........A..CD.E....D.CE.B` | 28 | 2 | 1/1 | 13.7 | 0 | West 4@39, East 5@38 |
| 40 | REFRAIN-ADJ | `A...A...B....B` | 14 | 2 | 1/1 | 2.1 | 2 | East 2@49, East 2@84 |
| 41 | PARTIAL | `A..B...B......C.....D...D..CA` | 29 | 2 | 1/1 | 9.9 | 0 | East 4@70, West 4@73 |
| 42 | PARTIAL | `A...A......B.....C...C..B..C` | 28 | 2 | 1/1 | 9.9 | 0 | East 4@73, West 4@76 |
| 43 | PARTIAL | `A..BA.........B..CD......D.C` | 28 | 2 | 1/1 | 9.9 | 0 | West 4@36, East 5@35 |
| 44 | PARTIAL | `A..........A..BC.D....C.BD` | 26 | 2 | 1/1 | 9.8 | 0 | West 4@39, East 5@38 |
| 45 | PARTIAL | `A...........BC.D....C.BD.A` | 26 | 2 | 1/1 | 9.8 | 0 | West 4@41, East 5@40 |
| 46 | PARTIAL | `AB.C....B.AC..B` | 15 | 2 | 1/1 | 9.7 | 0 | East 4@51, East 5@52 |
| 47 | PARTIAL | `A........A.B.C..C.B` | 19 | 2 | 1/1 | 5.9 | 1 | West 1@59, East 3@90 |
| 48 | PARTIAL | `A.....A..B....C...C........B` | 28 | 2 | 1/1 | 6.0 | 0 | East 4@59, East 5@60 |
| 49 | PARTIAL | `A..BA.........B...C......C` | 26 | 2 | 1/1 | 6.0 | 0 | West 4@36, East 5@35 |
| 50 | PARTIAL | `A..........A..BC......C.B` | 25 | 2 | 1/1 | 6.0 | 0 | West 4@39, East 5@38 |
| 51 | PARTIAL | `A.....B...B..A..B` | 17 | 2 | 1/1 | 5.9 | 0 | East 4@84, West 4@87 |
| 52 | PARTIAL | `A.B....A..B..A` | 14 | 2 | 1/1 | 5.9 | 0 | East 4@52, East 5@53 |
| 53 | NESTED | `AB......A.C.D.BD.C` | 18 | 3 | 3/3 | 15.0 | 2 | East 1@30, West 1@30, East 2@35 |
| 54 | PARTIAL | `A........A...B..B` | 17 | 2 | 1/1 | 2.1 | 1 | West 1@59, East 3@90 |
| 55 | PARTIAL | `A..........A...B......B` | 23 | 2 | 1/1 | 2.2 | 0 | West 4@39, East 5@38 |
| 56 | PARTIAL | `A.....A.......B...B` | 19 | 2 | 1/1 | 2.1 | 0 | East 4@59, East 5@60 |
| 57 | NESTED | `A.BA..B` | 7 | 6 | 14/15 | 8.0 | 4 | East 1@42, East 1@70, West 1@42, West 1@72, +2 |
| 58 | PARTIAL | `A....B..A..B` | 12 | 2 | 1/1 | 2.1 | 0 | East 4@54, East 5@55 |
| 59 | NESTED | `A........B.C.AC.B` | 17 | 3 | 3/3 | 9.2 | 2 | East 1@31, West 1@31, East 2@36 |
| 60 | NESTED | `A....B...B........A` | 19 | 3 | 3/3 | 3.5 | 0 | East 4@68, West 4@71, East 5@69 |
| 61 | NESTED | `A..BA.........B` | 15 | 2 | 1/1 | 2.1 | 0 | West 4@36, East 5@35 |

## Tier summary

- **CERTIFIED**: 2
- **LIKELY**: 19
- **REFRAIN-ADJ**: 14
- **PARTIAL**: 21
- **NESTED**: 5
