# from loguru import logger

from PyQt6.QtCore import Qt, pyqtSlot, QSize, QObject, QPoint, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QWidget, QFrame, QSplitter, QSizePolicy

from ..core import app_globals as ag
from .foldable import Foldable, MIN_HEIGHT
from .. import tug

class MouseEventFilter(QObject):
    resize_foldable = pyqtSignal(int, QPoint, int)  # QMouseEvent.Type, position & secno

    def __init__(self, widget: Foldable, seqno: int):
        super().__init__(widget)

        self._widget: Foldable = widget
        self.seq = seqno
        self._widget.installEventFilter(self)

    def eventFilter(self, obj: QObject, event: QMouseEvent) -> bool:
        typo = event.type()
        """
         2 QEvent.MouseButtonPress
         3 QEvent.MouseButtonRelease
         5 QEvent.MouseMove
        10 QEvent.Enter
        """
        if typo in (2, 3, 5, 10):
            pos = event.globalPosition().toPoint()
            # logger.info(f'{typo=}, {pos.y()=}')
            self.resize_foldable.emit(typo, pos, self.seq)
        return super().eventFilter(obj, event)


class FoldContainer(QSplitter):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.sizes0 = []
        self.y0 = 0
        self.above = self.below = 0    # 0 not defined yet
        self.good_for_resize = False
        self.setOrientation(Qt.Orientation.Vertical)
        self.setChildrenCollapsible(False)
        self.setOpaqueResize(True)      # rubberBand doesn't appear automatically
        self.setHandleWidth(0)          # handles aren't visible because width = 0
        self.ffs: list[Foldable] = []
        self.add_foldables()

        ff = self.ffs[-1]
        ff.ui.toFold.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        ff.ui.toFold.customContextMenuRequested.connect(ff.change_title)
        ag.signals.collapseSignal.connect(self.toggle_collapsed)
        ag.signals.hideSignal.connect(self.set_hidden)

        self._setup()

    def add_foldables(self):
        for i in range(4):
            ff = Foldable()
            ff.seqno = i
            ff.setMinimumSize(QSize(0, MIN_HEIGHT))
            ff.setObjectName(f"foldable_{i+1}")
            self.addWidget(ff)
            self.ffs.append(ff)

        self.spacer = QWidget()
        s_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        s_policy.setHorizontalStretch(0)
        s_policy.setVerticalStretch(0)
        self.spacer.setSizePolicy(s_policy)
        self.spacer.setMinimumHeight(0)
        self.addWidget(self.spacer)

    def visible_state(self):
        """   used in sho.py   """
        return [not ff.is_hidden for ff in self.ffs]

    def _setup(self):
        def set_titles():
            ttls = tug.qss_params['$FoldTitles']
            for i,ff in enumerate(self.ffs):
                ff.set_title(ttls[i])

        def setup_event_filter():
            for i in range(1, len(self.ffs)):
                filter = MouseEventFilter(self.handle(i), i)
                filter.resize_foldable.connect(self._resize_widget)

        self.setMinimumHeight(int(MIN_HEIGHT * 1.5))
        set_titles()
        setup_event_filter()

    def add_widget(self, w: QWidget, index: int) -> None:
        """   used in sho.py   """
        self.ffs[index].add_widget(w)

    def get_frames(self) -> list[QFrame]:
        """   used in sho.py   """
        return [ff.get_inner_frame() for ff in self.ffs]

    @pyqtSlot(int, bool)
    def toggle_collapsed(self, seq: int, state: bool):
        """   state:  True - collapsing, False - expanding   """
        ff = self.ffs[seq]

        self.setUpdatesEnabled(False)
        if self.spacer.height():
            szs = self.sizes()
            szs[seq] = self.spacer.height() + ff.ui.toFold.height()
        else:
            delta = ff.height_inner
            szs = (self.decrease_next, self.increase_next)[state](seq, delta)
        self.set_min_heights(szs)
        self.setSizes(szs)
        self.setUpdatesEnabled(True)

    def set_min_heights(self, sizes: list[int]):
        all_collapsed = True    # means that each item is collapsed or hidden
        for ff,hh in zip(self.ffs, sizes):
            if not ff.is_hidden:
                ff.setMinimumHeight(hh)
                all_collapsed &= ff.is_collapsed
        if all_collapsed:
            sizes[-1] = self.height() - sum(sizes[:-1])

    def increase_next(self, seq: int, delta: int):
        szs = self.sizes()
        szs[seq] -= delta
        ff_cnt = len(self.ffs)
        for k in range(ff_cnt-1, -1, -1):
            ff = self.ffs[k]
            if not (k == seq or ff.is_collapsed or ff.is_hidden):
                szs[k] += delta
                break
        return szs

    def decrease_next(self, seq: int, delta: int):
        szs = self.sizes()
        szs[seq] += delta
        dd = delta
        ff_cnt = len(self.ffs)
        for k in range(ff_cnt-1, -1, -1):
            ff = self.ffs[k]
            if not (k == seq or ff.is_collapsed or ff.is_hidden):
                if szs[k] - MIN_HEIGHT >= dd:
                    szs[k] -= dd
                    break
                else:
                    dd -= (szs[k] - MIN_HEIGHT)
                    szs[k] = MIN_HEIGHT
        else:
            szs[seq] -= dd
        return szs

    def restore_state(self, state: list):
        """
            restore state of container:
            0 - sizes of widgets in splitter
            1 - for each item in container:
            0 - is_collapsed: bool
            1 - is_hidden: bool
        """
        def set_hide_collapse():
            for ff,st in zip(self.ffs, state[1]):
                if st[0]:
                    ff.is_hidden = True
                if st[1]:
                    ff.ui.toFold.setChecked(True)

        ht = self.ffs[0].ui.toFold.height()
        if not state:
            hgt = ag.app.sho_rect.height()- ag.app.ui.left_top.height() - ag.app.ui.status.height()
            cnt = len(self.ffs)
            ee = hgt // cnt
            szs = [ee + hgt % cnt, *[ee] * (cnt-1)]
        else:
            szs = [0 if st[0] else ht if st[1] else hh for st,hh in zip(state[1], state[0])]

        self.setUpdatesEnabled(False)

        self.setSizes([*szs, 0])
        for ff,hh in zip(self.ffs, szs):
            if not ff.is_hidden:
                ff.height_inner = hh - ht
                ff.setMinimumHeight(hh)

        if state:
            set_hide_collapse()

        self.setUpdatesEnabled(True)

        for ff in self.ffs:
            ff.ui.toFold.toggled.connect(ff.on_click)

    def save_state(self) -> list:
        """
        function is used to collect data to save settings of state
        0 - width of container, it restore in parrent of FoldContainer instance
        1 - sizes of widgets in splitter
        2 - states of each widget in container: is_hidden, is_collapsed
        """
        ht = self.ffs[0].ui.toFold.height()
        szs = []
        for ff in self.ffs:
            szs.append(ff.height_inner + ht)
        return [szs, [(ff.is_hidden, ff.is_collapsed) for ff in self.ffs]]

    @pyqtSlot(bool, int)
    def set_hidden(self, state: bool, seq: int):
        """   state:  True - hide, False - show   """
        ff = self.ffs[seq]
        ff.is_hidden = state

        self.setUpdatesEnabled(False)

        if self.spacer.height():
            szs = self.sizes()
            szs[seq] = ff.ui.toFold.height() if ff.is_collapsed else self.spacer.height()
        else:
            delta = self.ffs[seq].height_inner
            delta = ff.ui.toFold.height()
            if not ff.is_collapsed:
                delta += ff.height_inner
            szs = (self.decrease_next, self.increase_next)[state](seq, self.spacer.height() or delta)

        self.set_min_heights(szs)
        self.setSizes(szs)

        self.setUpdatesEnabled(True)

    @pyqtSlot(int, QPoint, int)
    def _resize_widget(self, e_type: int, pos: QPoint, seq: int):
        {
            QMouseEvent.Type.MouseButtonPress: self.resize_start,
            QMouseEvent.Type.MouseButtonRelease: self.resize_end,
            QMouseEvent.Type.MouseMove: self.resize_wid,
            QMouseEvent.Type.Enter: self.hover_start,
        }[e_type](self.mapFromGlobal(pos).y(), seq)

    def resize_wid(self, y: int, seq: int):
        def resize_items() -> int:
            (incr_curr, decr_curr)[delta < 0]()
            apply_sizes()

        def apply_sizes():
            self.ffs[below].setMinimumHeight(szs[below])
            self.ffs[above].setMinimumHeight(szs[above])
            self.setSizes(szs)

        def decr_curr() -> int:
            """  delta < 0, move mouse down  """
            dd = MIN_HEIGHT - szs[below]
            vv = max(dd, delta)
            szs[below] += vv
            szs[above] -= vv
            if dd >= delta:
                self.below = self.next_below(below)
            if szs[above] >= self.sizes0[above]:
                ss = szs[above] - self.sizes0[above]
                szs[above] = self.sizes0[above]
                szs[below] += ss
                self.above = self.next_below(above)

        def incr_curr() -> int:
            """  delta > 0, move mouse up  """
            dd = szs[above] - MIN_HEIGHT
            vv = min(dd, delta)
            szs[below] += vv
            szs[above] -= vv
            if dd <= delta:
                self.above = self.next_above(above)
            if szs[below] >= self.sizes0[below]:
                ss = szs[below] - self.sizes0[below]
                szs[below] = self.sizes0[below]
                szs[above] += ss
                self.below = self.next_above(below)

        if not self.good_for_resize:
            return

        delta = self.y0 - y
        szs = self.sizes()
        above, below = self.above, self.below

        self.setUpdatesEnabled(False)
        resize_items()
        self.setUpdatesEnabled(True)

        self.y0 = self.ffs[seq].y()

    def resize_start(self, y: int, seq: int):
        if self.good_for_resize:
            self.ffs[seq].ui.fold_head.setStyleSheet(tug.get_dyn_qss("left_pane_split_pressed"))
            self.y0 = y
            self.above = self.next_above(seq)
            self.sizes0 = self.sizes()
            # no height limit for these two items
            self.sizes0[self.below] = self.sizes0[self.above] = 16777215

    def pointer_below(self, seq: int) -> int:
        return next((x.seqno for x in self.ffs[seq:] if not (x.is_hidden or x.is_collapsed)), 0)

    def next_below(self, seq: int) -> int:
        return next((x.seqno for x in self.ffs[seq+1:] if not (x.is_hidden or x.is_collapsed)), seq)

    def next_above(self, seq: int) -> int:
        """  if Ok result must be less than seq;  seq > 0  """
        return next((x.seqno for x in self.ffs[seq-1::-1] if not (x.is_hidden or x.is_collapsed))) if seq else 0

    def immediate_above(self, seq: int) -> bool:
        """
        returns True if immediate above item is not collapsed,
        generator is used because immediate above item may be hidden,
        next's default parameter (3) need if all above items is hidden
        """
        return next((not x.is_collapsed for x in self.ffs[seq-1::-1] if not x.is_hidden))

    def resize_end(self, y: int, seq: int):
        if self.good_for_resize:
            self.y0 = 0
            self.unsetCursor()
            self.ffs[seq].ui.fold_head.setStyleSheet(tug.get_dyn_qss("left_pane_split"))

    def hover_start(self, y: int, seq: int):
        """  seq > 0  --  always because of splitter  """
        self.below = self.pointer_below(seq)
        self.good_for_resize = (self.below >= seq) and self.immediate_above(seq)
