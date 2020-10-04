from typing import Callable, TypeVar, Any

import pymonad
import pymonad.either
from pymonad.either import M, S, T, Left, Right

N = TypeVar('N')


class Either(pymonad.either.Either[M, S]):
    f"""{pymonad.either.Either.__doc__}
    
    ---

    Expanded slightly to add some quality of life stuff.    
    """

    def lmap(self: 'Either[M, S]', function: Callable[[M], N]) -> 'Either[N, S]':
        if self.is_right():
            return self
        else:
            return self.__class__(None, (function(self.monoid[0]), False))

    @property
    def l_value(self: 'Either[M, Any]') -> M:
        return self.monoid[0]


setattr(pymonad.either, 'Either', Either)
