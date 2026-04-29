# wb_spi_mem_ctrl Register Map

Simple register map for sequential SPI memory block reads.

- Module: `wb_spi_mem_ctrl`
- Bus: `wishbone`

## Registers

| Name | Offset | Width | Access | Reset | Source | Description |
|---|---:|---:|---|---|---|---|
| `SPI_CTRL` | `0x00` | 8 | `rw` | `0x02` | `internal` | Control commands for transfer start/stop. |
| `SPI_STATUS` | `0x04` | 8 | `ro` | `0x00` | `external` | Status register for the SPI memory controller. |
| `MAX_FETCH_SIZE` | `0x08` | 8 | `rw` | `0xFF` | `internal` | Counter of bytes fetched so far. |
| `BYTES_FETCHED` | `0x0C` | 8 | `ro` | `0x00` | `external` | Counter of bytes fetched so far. |
| `IRQ_STATUS` | `0x10` | 8 | `rw` | `0x00` | `external` | Interrupt status flags. |
| `IRQ_ENABLE` | `0x14` | 2 | `rw` | `0x0` | `internal` | Interrupt enable controls. |

## `SPI_CTRL` (@ `0x00`)

Control commands for transfer start/stop.

| Property | Value |
|---|---|
| Offset | `0x00` |
| Width | `8` |
| Access | `rw` |
| Reset | `0x02` |
| Source | `internal` |

### Fields

| Bits | Name | Access | Pulse | Description |
|---:|---|---|---|---|
| `0` | `start` | `wo` | `true` | Write 1 to start a sequential read transfer. |
| `1` | `fetch_mode` | `rw` | `false` | 0 = Byte Fetch, 1 = Block Fetch mode. |

## `SPI_STATUS` (@ `0x04`)

Status register for the SPI memory controller.

| Property | Value |
|---|---|
| Offset | `0x04` |
| Width | `8` |
| Access | `ro` |
| Reset | `0x00` |
| Source | `external` |

### Fields

| Bits | Name | Access | Pulse | Description |
|---:|---|---|---|---|
| `0` | `spi_busy` | `ro` | `false` | High when a transfer is in progress. |
| `1` | `spi_error` | `ro` | `false` | High when a SPI error has occurred. |

## `MAX_FETCH_SIZE` (@ `0x08`)

Counter of bytes fetched so far.

| Property | Value |
|---|---|
| Offset | `0x08` |
| Width | `8` |
| Access | `rw` |
| Reset | `0xFF` |
| Source | `internal` |

### Fields

(No fields)

## `BYTES_FETCHED` (@ `0x0C`)

Counter of bytes fetched so far.

| Property | Value |
|---|---|
| Offset | `0x0C` |
| Width | `8` |
| Access | `ro` |
| Reset | `0x00` |
| Source | `external` |

### Fields

(No fields)

## `IRQ_STATUS` (@ `0x10`)

Interrupt status flags.

| Property | Value |
|---|---|
| Offset | `0x10` |
| Width | `8` |
| Access | `rw` |
| Reset | `0x00` |
| Source | `external` |

### Fields

| Bits | Name | Access | Pulse | Description |
|---:|---|---|---|---|
| `0` | `byte_done` | `rw1c` | `false` | Set when byte transfer is complete; write 1 to clear. |
| `1` | `block_done` | `rw1c` | `false` | Set when full block transfer is complete; write 1 to clear. |

## `IRQ_ENABLE` (@ `0x14`)

Interrupt enable controls.

| Property | Value |
|---|---|
| Offset | `0x14` |
| Width | `2` |
| Access | `rw` |
| Reset | `0x0` |
| Source | `internal` |

### Fields

| Bits | Name | Access | Pulse | Description |
|---:|---|---|---|---|
| `0` | `byte_done_en` | `rw` | `false` | Enables byte done irq output. |
| `1` | `block_done_en` | `rw` | `false` | Enables byte done irq output. |

## IRQ

Asserted when an interrupt is active

- Name: `irq`
- Condition:

```text
IRQ_STATUS.byte_done && IRQ_ENABLE.byte_done_en || IRQ_STATUS.block_done && IRQ_ENABLE.block_done_en
```
