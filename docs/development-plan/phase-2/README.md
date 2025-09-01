# Phase 2: 图像处理集成开发计划

**阶段**: Phase 2 of 3
**工期**: 2周 (Week 3-4)
**开始日期**: 2025-02-14
**结束日期**: 2025-02-28
**负责人**: 全栈开发者
**前置条件**: Phase 1 核心节点系统已完成

---

## 🎯 **阶段目标**

### **主要目标**
集成 OpenCV 图像处理能力，实现高精度的图像识别和匹配功能。

### **具体目标**
- 🖼️ 集成 OpenCV 图像处理库
- 🔍 实现多种图像匹配算法
- ⚡ 优化图像处理性能
- 🛠️ 完善图像处理节点
- 📊 建立图像处理测试框架

---

## 📋 **详细任务分解**

### **Week 3: OpenCV 集成和基础算法**

#### **Day 15-16: OpenCV 集成架构**

**任务 2.1: 图像处理核心模块**
```python
# 目标文件: bluev/vision/image_processor.py
class ImageProcessor:
    """图像处理核心类"""

    @staticmethod
    def load_image(path: str) -> np.ndarray
    @staticmethod
    def save_image(image: np.ndarray, path: str) -> bool
    @staticmethod
    def resize_image(image: np.ndarray, size: Tuple[int, int]) -> np.ndarray
    @staticmethod
    def convert_color_space(image: np.ndarray, conversion: str) -> np.ndarray
    @staticmethod
    def apply_threshold(image: np.ndarray, threshold: float) -> np.ndarray
```

**验收标准**:
- [ ] 支持常见图像格式 (PNG, JPG, BMP)
- [ ] 图像预处理功能完整
- [ ] 内存使用优化
- [ ] 错误处理健壮

**任务 2.2: 屏幕截图工具增强**
```python
# 目标文件: bluev/vision/screenshot_utils.py
class ScreenshotCapture:
    """屏幕截图工具类"""

    def __init__(self):
        self.monitors = self._detect_monitors()

    def capture_screen(self, monitor: int = 0) -> np.ndarray
    def capture_region(self, region: Tuple[int, int, int, int]) -> np.ndarray
    def capture_window(self, window_title: str) -> Optional[np.ndarray]
    def get_screen_size(self, monitor: int = 0) -> Tuple[int, int]
```

**验收标准**:
- [ ] 支持多显示器截图
- [ ] 区域截图功能准确
- [ ] 窗口截图功能稳定
- [ ] 截图速度 < 500ms

#### **Day 17-18: 图像匹配算法实现**

**任务 2.3: 模板匹配算法**
```python
# 目标文件: bluev/vision/template_matcher.py
class TemplateMatcher:
    """模板匹配算法实现"""

    def __init__(self, method: str = "TM_CCOEFF_NORMED"):
        self.method = getattr(cv2, method)

    def find_template(self, source: np.ndarray, template: np.ndarray,
                     threshold: float = 0.8) -> List[MatchResult]
    def find_best_match(self, source: np.ndarray, template: np.ndarray) -> MatchResult
    def find_all_matches(self, source: np.ndarray, template: np.ndarray,
                        threshold: float = 0.8) -> List[MatchResult]
```

**任务 2.4: 多尺度匹配**
```python
# 目标文件: bluev/vision/multiscale_matcher.py
class MultiScaleMatcher:
    """多尺度图像匹配"""

    def __init__(self, scale_range: Tuple[float, float] = (0.5, 2.0),
                 scale_steps: int = 10):
        self.scale_range = scale_range
        self.scale_steps = scale_steps

    def match_with_scaling(self, source: np.ndarray, template: np.ndarray,
                          threshold: float = 0.8) -> Optional[MatchResult]
```

**验收标准**:
- [ ] 模板匹配准确率 > 90%
- [ ] 支持多尺度匹配
- [ ] 匹配速度 < 2秒
- [ ] 支持多个匹配结果

#### **Day 19-21: 高级图像处理功能**

**任务 2.5: 图像预处理优化**
```python
# 目标文件: bluev/vision/image_enhancer.py
class ImageEnhancer:
    """图像增强和预处理"""

    def enhance_contrast(self, image: np.ndarray, alpha: float = 1.5) -> np.ndarray
    def adjust_brightness(self, image: np.ndarray, beta: int = 50) -> np.ndarray
    def apply_gaussian_blur(self, image: np.ndarray, kernel_size: int = 5) -> np.ndarray
    def apply_edge_detection(self, image: np.ndarray) -> np.ndarray
    def remove_noise(self, image: np.ndarray) -> np.ndarray
```

**任务 2.6: 颜色检测算法**
```python
# 目标文件: bluev/vision/color_detector.py
class ColorDetector:
    """颜色检测和分析"""

    def detect_color_range(self, image: np.ndarray,
                          lower_bound: Tuple[int, int, int],
                          upper_bound: Tuple[int, int, int]) -> np.ndarray
    def find_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[Tuple[int, int, int]]
    def calculate_color_histogram(self, image: np.ndarray) -> np.ndarray
```

**验收标准**:
- [ ] 图像增强效果明显
- [ ] 颜色检测准确可靠
- [ ] 处理速度满足要求
- [ ] 支持批量处理

### **Week 4: 节点完善和性能优化**

#### **Day 22-24: 图像处理节点完善**

**任务 2.7: FindImageNode 完整实现**
```python
# 目标文件: bluev/nodes/image/find_image_node.py (增强版)
@bluev_node("find_image", "image_processing")
class FindImageNode(BaseNode):
    """图像查找节点 (完整版)"""

    输入参数:
    - template_image: Union[np.ndarray, str]  # 模板图像或路径
    - source_image: Optional[np.ndarray] = None  # 源图像(默认截屏)
    - threshold: float = 0.8              # 匹配阈值
    - method: str = "TM_CCOEFF_NORMED"    # 匹配方法
    - multi_scale: bool = False           # 是否多尺度匹配
    - find_all: bool = False              # 是否查找所有匹配
    - region: Optional[Tuple[int, int, int, int]] = None  # 搜索区域

    输出结果:
    - found: bool                         # 是否找到
    - matches: List[MatchResult]          # 匹配结果列表
    - best_match: Optional[MatchResult]   # 最佳匹配
    - processing_time: float              # 处理时间
```

**任务 2.8: 新增图像处理节点**
```python
# 目标文件: bluev/nodes/image/image_enhance_node.py
@bluev_node("image_enhance", "image_processing")
class ImageEnhanceNode(BaseNode):
    """图像增强节点"""

# 目标文件: bluev/nodes/image/color_detect_node.py
@bluev_node("color_detect", "image_processing")
class ColorDetectNode(BaseNode):
    """颜色检测节点"""

# 目标文件: bluev/nodes/image/region_select_node.py
@bluev_node("region_select", "image_processing")
class RegionSelectNode(BaseNode):
    """区域选择节点"""
```

**验收标准**:
- [ ] 所有图像处理节点功能完整
- [ ] 参数配置灵活易用
- [ ] 错误处理完善
- [ ] 性能满足要求

#### **Day 25-26: 性能优化和缓存**

**任务 2.9: 图像处理性能优化**
```python
# 目标文件: bluev/vision/performance_optimizer.py
class ImageProcessingOptimizer:
    """图像处理性能优化器"""

    def __init__(self):
        self.template_cache = {}
        self.result_cache = {}

    def cache_template(self, template_path: str, template: np.ndarray)
    def get_cached_template(self, template_path: str) -> Optional[np.ndarray]
    def optimize_image_size(self, image: np.ndarray, max_size: int = 1920) -> np.ndarray
    def parallel_process(self, images: List[np.ndarray],
                        processor: Callable) -> List[Any]
```

**任务 2.10: 内存管理优化**
```python
# 目标文件: bluev/vision/memory_manager.py
class ImageMemoryManager:
    """图像内存管理器"""

    def __init__(self, max_cache_size: int = 100):
        self.max_cache_size = max_cache_size
        self.cache = {}

    def add_to_cache(self, key: str, image: np.ndarray)
    def get_from_cache(self, key: str) -> Optional[np.ndarray]
    def clear_cache(self)
    def get_memory_usage(self) -> float
```

**验收标准**:
- [ ] 图像处理速度提升 50%
- [ ] 内存使用稳定 (< 256MB)
- [ ] 缓存命中率 > 70%
- [ ] 支持并行处理

#### **Day 27-28: 测试和文档**

**任务 2.11: 图像处理测试套件**
```python
# 目标文件: tests/unit/test_image_processing.py
class TestImageProcessor:
    def test_image_loading()
    def test_image_preprocessing()
    def test_template_matching()
    def test_multiscale_matching()

# 目标文件: tests/integration/test_image_workflow.py
def test_screenshot_find_click_workflow():
    """测试完整的图像处理工作流"""

def test_batch_image_processing():
    """测试批量图像处理"""
```

**任务 2.12: 性能基准测试**
```python
# 目标文件: tests/performance/test_image_performance.py
def benchmark_template_matching():
    """模板匹配性能基准测试"""

def benchmark_image_preprocessing():
    """图像预处理性能基准测试"""
```

**验收标准**:
- [ ] 单元测试覆盖率 ≥ 85%
- [ ] 性能测试通过
- [ ] 集成测试稳定
- [ ] 文档完整准确

---

## 📊 **完成定义 (Definition of Done)**

### **功能标准**
- [ ] 图像匹配准确率 > 90%
- [ ] 支持多种图像格式和尺寸
- [ ] 图像处理速度 < 2秒/次
- [ ] 内存使用稳定 (< 256MB)

### **技术标准**
- [ ] OpenCV 集成完整稳定
- [ ] 所有图像处理节点正常工作
- [ ] 性能优化效果明显
- [ ] 缓存机制有效

### **质量标准**
- [ ] 单元测试覆盖率 ≥ 85%
- [ ] 性能基准测试通过
- [ ] 代码质量达标
- [ ] 文档完整

---

## 🚨 **风险和缓解措施**

### **技术风险**
- **风险**: OpenCV 版本兼容性问题
- **缓解**: 锁定 OpenCV 版本，充分测试

### **性能风险**
- **风险**: 大图像处理性能瓶颈
- **缓解**: 图像尺寸优化，并行处理

### **质量风险**
- **风险**: 图像匹配准确率不达标
- **缓解**: 多算法融合，参数调优

---

## 📈 **里程碑检查点**

- **Day 18**: OpenCV 集成完成，基础算法可用
- **Day 24**: 所有图像处理节点实现完成
- **Day 28**: Phase 2 完整交付，性能达标

---

**文档状态**: ✅ 已完成
**上一阶段**: [Phase 1: 核心节点系统](../phase-1/README.md)
**下一阶段**: [Phase 3: 基础UI实现](../phase-3/README.md)
