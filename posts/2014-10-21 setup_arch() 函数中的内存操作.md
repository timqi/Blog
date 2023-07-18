- tags: [linux](/tags.md#linux)
- date: 2014-10-21

# setup_arch() 函数中的内存操作

setup_arch() 函数位于 `arch/x86/kernel` 目录中，完成设置启动内核过程中与硬件相关的部分，本篇主要讲述其中与内存管理有关的部分。

首先 setup_memory_map() 函数从系统 BIOS 中读取内存相关物理信息并存到 e820 结构体中，parse_setup_data() 函数解析内核参数，最后 e820_reserve_setup_data() 函数更新 e820 信息。相关结构如下所示：

```c
struct e820entry {
	__u64 addr;	/* start of memory segment */
	__u64 size;	/* size of memory segment */
	__u32 type;	/* type of memory segment */
} __attribute__((packed));

struct e820map {
	__u32 nr_map;
	struct e820entry map[E820_X_MAX];
} e820;

``` c
max_pfn = e820_end_of_ram_pfn();

```

e820_end_of_ram_pfn() 函数调用 e820_end_pfn(MAX_ARCH_PFN, E820_RAM) 得到可用物理内存中**最大页面数**并存于 max_pfn 变量中。

```c
for (i = 0; i < e820.nr_map; i++) {
    struct e820entry *ei = &e820.map[i];
    unsigned long start_pfn;
    unsigned long end_pfn;
    if (ei->type != type)
    continue;

    start_pfn = ei->addr >> PAGE_SHIFT;
    end_pfn = (ei->addr + ei->size) >> PAGE_SHIFT;

    if (start_pfn >= limit_pfn)
        continue;
    if (end_pfn > limit_pfn) {
        last_pfn = limit_pfn;
        break;
    }
    if (end_pfn > last_pfn)
        last_pfn = end_pfn;
    }
}

```

求得 max_pfn 值得再循环如上，从 e820 结构体中依次一处存储块判断是否满足条件，如果满足则更新最大页框值。

reserve_brk();、reserve_initrd();  预留出相关寄存器与启动镜像的相关空间，然后调用 initmem_init(0, max_pfn); 函数初始化并建立 bootmem 位图表示的启动内存管理器进行系统启动早期的内存管理，它的原理是使用一位表示一个页框是否被占用。

```c
reserve_crashkernel();
dma32_reserve_bootmem();
reserve_ibft_region();

```

上面三个函数继续在 bootmem 管理器中预留出相关空间供后续使用，接下来系统需要建立页框并对 buddy 系统初始化，然后释放 bootmem 将内存管管理的相关功能交给 buudy 管理。

```c
x86_init.paging.pagetable_setup_start(swapper_pg_dir);
paging_init();
x86_init.paging.pagetable_setup_done(swapper_pg_dir);

```