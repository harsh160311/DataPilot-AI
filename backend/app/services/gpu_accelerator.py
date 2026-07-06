from app.config import settings


class GPUAccelerator:
    def __init__(self):
        self.enabled = settings.ENABLE_GPU
        self._cudf = None
        self._cuml = None
        self._cupy = None

        if self.enabled:
            self._try_init_gpu()

    def _try_init_gpu(self):
        try:
            import cudf
            self._cudf = cudf
        except ImportError:
            self.enabled = False

        try:
            import cuml
            self._cuml = cuml
        except ImportError:
            pass

        try:
            import cupy as cp
            self._cupy = cp
        except ImportError:
            pass

    def to_gpu(self, df):
        if not self.enabled or self._cudf is None:
            return None
        try:
            return self._cudf.DataFrame.from_pandas(df)
        except Exception:
            return None

    def from_gpu(self, gpu_df):
        if gpu_df is None:
            return None
        try:
            return gpu_df.to_pandas()
        except Exception:
            return None

    def accelerate_aggregation(self, df, group_col, agg_col, agg_func="mean"):
        gpu_df = self.to_gpu(df)
        if gpu_df is not None:
            try:
                result = gpu_df.groupby(group_col)[agg_col].agg(agg_func)
                return self.from_gpu(result.reset_index())
            except Exception:
                pass
        return None

    def describe_gpu(self, df):
        gpu_df = self.to_gpu(df)
        if gpu_df is not None:
            try:
                return gpu_df.describe()
            except Exception:
                pass
        return None

    def is_available(self):
        return self.enabled and self._cudf is not None

    def get_stats(self):
        return {
            "enabled": self.enabled,
            "cudf_available": self._cudf is not None,
            "cuml_available": self._cuml is not None,
            "cupy_available": self._cupy is not None,
        }


gpu_accelerator = GPUAccelerator()
