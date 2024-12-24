from functools import reduce
from operator import add

from PyQt6.QtCore import QObject, QPoint, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QMouseEvent, QResizeEvent
from PyQt6.QtWidgets import QWidget

from ..core import app_globals as ag
from .foldable import Foldable
from .ui_fold_container import Ui_Foldings
from .. import tug

MIN_HEIGHT = 62


class MouseEventFilter(QObject):
    resize_foldable = pyqtSignal(int, QPoint, int)  # QMouseEvent.Type, position & secno

    def __init__(self, widget: QWidget, seq: int):
        super().__init__(widget)

        self.pressed: bool = False
        self.seqno: int = seq

        self._widget: QWidget = widget
        self._widget.installEventFilter(self)

    def eventFilter(self, obj: QObject, event_: QMouseEvent) -> bool:
        if obj is self._widget:
            to_emit = False

            if event_.type() in (QMouseEvent.Type.Enter,
                                 QMouseEvent.Type.Leave,
                                ):
                self.resize_foldable.emit(event_.type(), QPoint(0, 0), self.seqno)
            elif event_.type() == QMouseEvent.Type.MouseButtonPress:
                to_emit = True
                self.pressed = True
            elif event_.type() == QMouseEvent.Type.MouseButtonRelease:
                to_emit = True
                self.pressed = False
            elif (event_.type() == QMouseEvent.Type.MouseMove) and self.pressed:
                to_emit = True

            if to_emit:
                self.resize_foldable.emit(event_.type(),
                    event_.globalPosition().toPoint(), self.seqno)
        return super().eventFilter(obj, event_)


class FoldState():
    __slot__ = ("__height", "__is_collapsed", "wid", "__is_hidden")

    def __init__(self, widget: Foldable):
        self.wid: Foldable = widget
        self.__height: int = 0
        self.__is_collapsed: bool = False
        self.__is_hidden: bool = False

    @property
    def is_collapsed(self) -> bool:
        return self.__is_collapsed

    @is_collapsed.setter
    def is_collapsed(self, val: bool):
        self.__is_collapsed = val
        self.reset_height()

    def reset_height(self):
        if self.__is_collapsed:
            self.set_collapsed_height()
        else:
            self.set_default_height()

    def set_collapsed_height(self):
        self.wid.setMinimumHeight(self._collapsed_height())

    def _collapsed_height(self) -> int:
        hh = self.wid.ui.fold_head.height()
        if not self.wid.ui.decorator.isHidden():
            hh += self.wid.ui.decorator.height()
        return hh

    @property
    def is_hidden(self) -> bool:
        return self.__is_hidden

    @is_hidden.setter
    def is_hidden(self, val:bool):
        self.__is_hidden = val
        self.wid.setVisible(not val)
        if not self.__is_hidden:
            self.reset_height()

    @property
    def height(self) -> int:
        if self.is_hidden:
            return 0
        if self.is_collapsed:
            return self._collapsed_height()
        return self.__height

    def store_height(self) -> int:
        return self.__height

    @height.setter
    def height(self, height: int):
        self.__height = height
        self.wid.setMinimumHeight(height)

    def set_default_height(self):
        if self.__height < MIN_HEIGHT:
            self.__height = MIN_HEIGHT
        self.wid.setMinimumHeight(self.__height)


class FoldContainer(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        Foldable.set_decorator_qss(tug.get_dyn_qss('decorator', -1))

        self.height_ = 0

        self.ui = Ui_Foldings()
        self.ui.setupUi(self)
        self.widgets: list[FoldState] = [FoldState(getattr(self.ui, m))
            for m in dir(self.ui) if type(getattr(self.ui, m)) is Foldable]

        ag.fold_states = self.widgets

        self.__first_visible: int = -1

        self._setup()

    @property
    def first_visible(self) -> int:
        return self.__first_visible

    @first_visible.setter
    def first_visible(self, seq: int):
        if self.__first_visible != seq and self.__first_visible >= 0:
            self.reset_decoration(self.__first_visible, True)
        self.__first_visible = seq
        self.reset_decoration(seq, False)

    def reset_decoration(self, seq: int, val: bool):
        self.widgets[seq].wid.set_decoration(val)
        if self.widgets[seq].is_collapsed:
            self.widgets[seq].set_collapsed_height()

    def _setup(self):
        self.ui.scrollArea.setMinimumHeight(int(MIN_HEIGHT * 1.5))

        self._set_titles()

        self._connect_signal()
        self._setup_event_filter()

    def set_qss_fold(self, qss: list):
        self.widgets[0].wid.set_decorator_qss(qss)

    def _setup_event_filter(self):
        self._filters = []
        for i,ff in enumerate(self.widgets):
            filter = MouseEventFilter(ff.wid.ui.decorator, i)
            filter.resize_foldable.connect(self._resize_widget)
            self._filters.append(filter)

    def _connect_signal(self):
        ag.signals_.collapseSignal.connect(self._toggle_collapsed)
        ag.signals_.hideSignal.connect(self.set_hidden)

    def _shown(self) -> int:
        """
        returns number of not hidden widgets
        """
        return sum((1 for ff in self.widgets if not (ff.is_hidden)))

    def shown_not_collapsed(self) -> int:
        """
        returns number of not hidden and not collapsed widgets
        """
        return sum((1 for ff in self.widgets if not (ff.is_hidden or ff.is_collapsed)))

    def _set_titles(self):
        ttls = tug.qss_params['$FoldTitles'].split(',')
        for i,ff in enumerate(self.widgets):
            ff.wid.set_title(ttls[i])

    def add_widget(self, w: QWidget, index: int) -> None:
        self.widgets[index].wid.add_widget(w)

    def get_widgets(self) -> list[QWidget]:
        return [w.wid.get_inner_widget() for w in self.widgets]

    def _expand_stretch(self, expand: bool):
        if expand:
            height = self.height_ - sum((ff.height for ff in self.widgets))
        else:
            height = 0
            if self.shown_not_collapsed() == 1:
                self.expand_first()

        self.ui.contents.layout().itemAt(
            len(self.widgets)
        ).spacerItem().changeSize(20, height)

    def expand_first(self):
        first = [ff for ff in self.widgets if not (ff.is_collapsed or ff.is_hidden)]
        if first:
            height = self.height_ - sum((ff.height for ff in self.widgets if ff is not first[0]))
            first[0].height = height

    @pyqtSlot(QObject, bool)
    def _toggle_collapsed(self, ff: Foldable, to_collapse: bool):
        """
        update view in case of collapse / expand one widget
        seq:  sequence number of widget
        collapsing:  True, False - expanding
        """
        seq = self._get_seq(ff)
        self.process_collapse(seq, to_collapse)

    def process_collapse(self, seq: int, to_collapse: bool):
        self.widgets[seq].is_collapsed = to_collapse

        if to_collapse:
            self._collapse_current(seq)
        else:
            self._expand_current(seq)

    def _collapse_current(self, seq: int):
        """
        seq is sequence number of widget to be collapsed
        """
        if self.shown_not_collapsed() == 0:
            self._expand_stretch(True)
        else:
            self._increase_next(seq)

    def _expand_current(self, seq: int):
        if self.shown_not_collapsed() == 1:  # all widgets are collapsed yet
            self._expand_stretch(False)
        else:
            # self.widgets[seq].set_default_height()
            self._decrease_next(seq)

    def _increase_next(self, seq: int):
        delta = self.height_ - self._actual_height()
        if delta <= 0:
            return

        for ff in (self.widgets[seq+1:] + self.widgets[seq-1::-1] if seq else self.widgets[seq+1:]):
            if ff.is_collapsed or ff.is_hidden:
                continue

            ff.height = ff.height + delta
            break

    def _decrease_next(self, seq: int):
        delta = self.height_ - self._actual_height()

        for ff in (self.widgets[seq+1:] + self.widgets[seq-1::-1] if seq else self.widgets[seq+1:]):
            if delta >= 0:
                break
            if ff.is_collapsed or ff.is_hidden:
                continue
            d2 = ff.height + delta
            if d2 < MIN_HEIGHT:
                delta = d2 - MIN_HEIGHT
                ff.height = MIN_HEIGHT
            else:
                ff.height = d2
                break
        else:
            self.widgets[seq].height += delta

    def _get_seq(self, ff: Foldable) -> int:
        return [i for i,gg in enumerate(self.widgets) if gg.wid is ff][0]

    def restore_state(self, state: list):
        """
        restore state of container:
        - number of first visible widget
        - height of container
        - for each widget in container:
          - is_collapsed: bool
          - is_hidden: bool
          - height: int
        """
        if state[0] is None:
            return

        self.first_visible = int(state[0])
        self.height_ = int(state[1])
        st1 = state[2:]

        for i, ff in enumerate(self.widgets):
            ff.height = st1[i][2]
            if st1[i][1]:
                ff.is_collapsed = True
                ff.wid.ui.toFold.setChecked(True)
                ff.wid.toggle_collapse()
            if st1[i][0]:
                ff.is_hidden = True

        _not_collapsed = self.shown_not_collapsed()
        if _not_collapsed <= 1:
            self._expand_stretch(_not_collapsed == 0)

    def save_state(self) -> list:
        """
        function is used to collect data to save settings of state
        - width of container, it restore in parrent of the widget
        - first_visible - number of first wisible widget in container
        - height - height of container, it also set in the resize event,
          but this value need in the restore_state method which
          is called before resize event
        - states of each widget in container:
          is_hidden, is_collapsed, and height
        """
        state = [self.width(), self.first_visible, self.height_]

        for ff in self.widgets:
            state.append(
                (ff.is_hidden, ff.is_collapsed, ff.store_height())
            )
        return state

    @pyqtSlot(bool, int)
    def set_hidden(self, to_show: bool, seq: int):
        self.widgets[seq].is_hidden = not to_show

        if self.shown_not_collapsed() == 0:
            self._expand_stretch(True)
            return

        self.show_hide(to_show, seq)

        if self._shown():
            self.reset_first_visible(seq)

    def show_hide(self, to_show: bool, seq: int):
        if to_show:
            if self.shown_not_collapsed() == 1:
                self._expand_stretch(False)
            else:
                self._decrease_next(seq)
        else:
            self._increase_next(seq)

    def reset_first_visible(self, seq: int):
        visibles = [i for i,ff in enumerate(self.widgets) if not ff.is_hidden]

        if visibles:
            self.first_visible = (
                seq if seq == visibles[0] else visibles[0] )

    def _actual_height(self) -> int:
        return reduce(add, (
            (ff.height for ff in self.widgets if not ff.is_hidden)
            ), 0
        )

    @pyqtSlot(QResizeEvent)
    def resizeEvent(self, a0: QResizeEvent) -> None:
        """
        change all widgets' height
        according the change of container height
        """
        hh = a0.size().height()

        if self.shown_not_collapsed() == 0:
            self.height_ = hh
            self._expand_stretch(True)
        else:
            self.resize_widgets(hh - self._actual_height())

        self.height_ = hh
        return super().resizeEvent(a0)

    def resize_widgets(self, delta: int):
        """
        recalculate each widgets' height by "the same" amount
        according the change of container height
        """
        if delta == 0:
            return
        if delta > 0:
            self.increase_widgets(delta)
        else:
            self.decrease_widgets(delta)

    def decrease_widgets(self, delta: int):
        nn = self.shown_not_collapsed()
        dd = delta // nn
        rr = 0

        for ff in self.widgets:
            if ff.is_hidden or ff.is_collapsed:
                continue

            hh = ff.height + dd
            if hh < MIN_HEIGHT:
                ff.height = MIN_HEIGHT
                rr += hh - MIN_HEIGHT
            else:
                ff.height = hh

        rr += delta % nn
        if rr:   # -nn < rr < nn
            self.add_remainder(rr)

    def add_remainder(self, remainder: int):
        """
        abs value of remainder is always less then number of widgets
        add 1 to each widget heigh until remainder runs out
        """
        if remainder == 0:
            return

        def increament() -> int:
            nonlocal remainder
            inc = 1 if remainder > 0 else -1
            remainder -= inc
            return inc

        if remainder < 0:
            remain = [ff for ff in self.widgets if not (
                ff.is_collapsed or ff.is_hidden) and ff.height > MIN_HEIGHT]
        else:
            remain = [ff for ff in self.widgets if not (
                ff.is_collapsed or ff.is_hidden)]

        for ff in remain:
            ff.height += increament()
            if remainder == 0:
                break

    def increase_widgets(self, delta: int):
        nn = self.shown_not_collapsed()
        dd = delta // nn

        for ff in self.widgets:
            if ff.is_hidden or ff.is_collapsed:
                continue
            ff.height += dd

        if rr := delta % nn:  # rr alwais >= 0 because nn > 0
            self.add_remainder(rr)

    @pyqtSlot(int, QPoint, int)
    def _resize_widget(self, e_type: int, pos: QPoint, seq: int):
        self.cur_pos = self.mapFromGlobal(pos)
        choice_ = {QMouseEvent.Type.MouseMove: self._resize,
                   QMouseEvent.Type.MouseButtonPress: self._resize_start,
                   QMouseEvent.Type.MouseButtonRelease: self._resize_end,
                   QMouseEvent.Type.Enter: self._hover_start,
                   QMouseEvent.Type.Leave: self._hover_end,
                   }
        choice_[e_type](self.cur_pos.y(), seq)

    def _resize_start(self, y: int, seq: int):
        self.y0 = y

    def _resize(self, y: int, seq: int):
        first, last = self.first_last()
        if (seq <= first) or (seq > last):
            return

        self.setUpdatesEnabled(False)
        self._resize_fold(seq, y)
        self.setUpdatesEnabled(True)

    def _resize_end(self, y: int, seq: int):
        if seq == self._first_uncollapsed():
            return
        self.unsetCursor()

    def _resize_fold(self, seq: int, y: int):
        if y > self.y0:
            self._decrease_current(seq, y)
        elif y < self.y0:
            self._increase_current(seq, y)

    def _decrease_current(self, seq: int, y: int):
        """
        y > self.y0,
        increase first uncollapsed widget above current one
        -- decrease current widget and bellow current
        """
        above: FoldState = self._find_above(seq)
        if not above:
            return self.y0

        # y > self.y0
        dd = delta = y - self.y0
        for ff in self.widgets[seq:]:
            dd = self._decrease_one(ff, dd)
            if dd == 0:
                break

        above.height += delta - dd
        self.y0 += delta - dd

    def _find_above(self, seq: int) -> FoldState:
        for ff in self.widgets[seq-1::-1]:
            if not (ff.is_collapsed or ff.is_hidden):
                return ff
        return None

    def _increase_current(self, seq: int, y: int):
        """
        y < self.y0,
        increase current widget
           or first uncollapsed widget bellow current
        -- decrease widgets above current one
        """
        to_increase: FoldState = self._find_below(seq)
        if not to_increase:
            return self.y0

        # y < self.y0
        dd = delta = self.y0 - y
        for ff in self.widgets[seq-1::-1]:   # always seq > 0
            dd = self._decrease_one(ff, dd)
            if dd == 0:
                break

        to_increase.height += delta - dd
        self.y0 -= delta + dd

    def _find_below(self, seq: int) -> FoldState:
        """
        find first uncollapsed widget starting from seq-th
        seq is a number of current widget
        """
        for ff in self.widgets[seq:]:
            if not (ff.is_collapsed or ff.is_hidden):
                return ff
        return None

    def _decrease_one(self, ff: FoldState, delta: int) -> int:
        """
        decrease height of one widget
        ff:    - FoldState object corresponds to current widget
        delta: - how much to decrease
        return:  remaining delta
        """
        if ff.is_collapsed or ff.is_hidden:
            return delta
        s = min(delta, ff.height - MIN_HEIGHT)
        ff.height -= s

        delta -= s
        return delta

    def _hover_start(self, y: int, seq: int):
        first, last = self.first_last()

        if (seq > first) and (seq <= last):
            self.widgets[seq].wid.set_hovering(True)
            self.setCursor(Qt.CursorShape.SizeVerCursor)

    def first_last(self) -> tuple[int, int]:
        first = self._first_uncollapsed()
        return first, self._last_uncollapsed(first)

    def _first_uncollapsed(self) -> int:
        for i, ff in enumerate(self.widgets):
            ff.wid.set_hovering(False)
            if not (ff.is_collapsed or ff.is_hidden):
                break
        return i

    def _last_uncollapsed(self, first: int) -> int:
        seq = 0
        for ff in self.widgets[:first:-1]:
            if not (ff.is_collapsed or ff.is_hidden):
                seq = self._get_seq(ff.wid)
                break
            ff.wid.set_hovering(False)
        return seq

    def _hover_end(self, y: int, seq: int):
        self.unsetCursor()
