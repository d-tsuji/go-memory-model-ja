Introduction
------------

Goのメモリモデルは、ある変数に対して、あるゴルーチンから変数に書き込みされた値を、別のゴルーチンが参照できることを保証する条件を示します。

Advice
------

複数のゴルーチンによって同時にアクセスされるデータを変更するプログラムは、シリアルにアクセスする必要があります。

アクセスをシリアル化するには、チャネルや ``sync`` パッケージや ``sync/atomic`` パッケージといった同期プリミティブを用いてデータを保護する必要があります。

プログラムの動作を理解するためにこのドキュメントの残りを読む必要がある場合は、あまりにも賢いです。

プログラムの振る舞いを理解するために本ドキュメントを読むことは、十分に役に立ちます。

.. todo:: Don't be clever.(どういう意味?)

Happens Before
--------------

1つのゴルーチン内で、読み取りと書き込みは、プログラムで指定された順序で実行されたかのように動作する必要があります。 つまり、コンパイラとプロセッサは、リオーダーによって言語仕様で定義されているようなゴルーチンの振る舞いを変えることがない場合に限り、単一のゴルーチンで実行された読み書きをリオーダーすることができます。リオーダーのため、あるゴルーチンで観測される実行順序は、別のゴルーチンで認識される順序と異なる場合があります。例えば、あるゴルーチンが ``a = 1; b = 2;`` と実行するとき、別のゴルーチンは ``a`` の値が更新される前に ``b`` の値が更新されていることを観測するかもしれません。

読み取りと書き込みの要件を指定するために、Goのプログラムでのメモリ操作の実行に関する半順序関係を定義します。 イベントe1がイベントe2の前に発生する場合、e2はe1の後に発生すると言います。 また、e1がe2の前に発生せず、e2の後に発生しない場合、e1とe2は同時に発生します。

単一のゴルーチン内では、半順序関係はプログラムによって表される順序です。

``v`` への更新 ``w`` を変数 ``v`` の参照 ``r`` が認識できるのは次の両方が成り立つ場合です。

#. w は r の前に発生する
#. w の後に r の前に ``v`` に対する別の更新 w' がない

変数 ``v`` の参照 r が v への特定の更新 w を認識することを保証するには、r が認識できる更新が w のみであることを確実にする必要があります。つまり、次の両方が成り立つ場合、 r は w を認識できることが保証されます。

#. r の前に w が発生する
#. 共有変数 ``v`` への任意の更新が w の前に発生するか r の後に発生する

この条件のペアは、最初のペアよりも強力です。 w または r と同時に発生する他の更新がないことが必要です。

単一のゴルーチン内では、同時実行性がないため、2つの定義は同等です。参照 r は、v への最新の更新 w によって更新された値を認識します。複数のゴルーチンが共有変数 v にアクセスする場合、必ず同期イベントを使用して、望ましい更新結果を参照が確実に認識するよう半順序関係の条件を成立させる必要があります。

v の型のゼロ値を用いて変数 v を初期化する場合は、メモリモデルの中では更新として動作します。

そのマシンの一語より大きい値の参照および更新は、順不同の複数のマシンワードサイズの処理として振舞います。

Synchronization
---------------

Initialization
~~~~~~~~~~~~~~

プログラムの初期化は単一のゴルーチンで実行されますが、そのゴルーチンは同時に実行される別のゴルーチンを作成することがあります。

パッケージ p がパッケージ q をインポートする場合、 q の init 関数は、任意の p の開始よりも前に完了します。

関数 ``main.main`` の開始は、すべての ``init`` 関数が完了した後に発生します。

Goroutine creation
~~~~~~~~~~~~~~~~~~

新しいゴルーチンを開始する ``go`` ステートメントは、ゴルーチンの実行が始まる前に発生します。

例として次のプログラムを見てみます。

.. code-block:: go

    var a string
    
    func f() {
        print(a)
    }
    
    func hello() {
        a = "hello, world"
        go f()
    }


``hello`` を呼び出すと、未来のある時点(おそらく ``hello`` が戻った後)で「hello、world」が出力されます。

Goroutine destruction
~~~~~~~~~~~~~~~~~~~~~

ゴルーチンの終了は、プログラム内のイベントの前に発生することが保証されていません。例として以下のプログラムを見てみます。

::

       var a string
       
       func hello() {
           go func() { a = "hello" }()
           print(a)
       }
       

a への割り当ての後に同期イベントが続くことはないため、他のゴルーチンによって認識されることは保証されません。実際、意欲的なコンパイラーは ``go`` ステートメント全体を削除する場合があります。

ゴルーチンの影響を別のゴルーチンで観察する必要がある場合は、ロックやチャネル通信などの同期メカニズムを使用して、相対的な順序を確立します。

Channel communication
~~~~~~~~~~~~~~~~~~~~~

Channel communication is the main method of synchronization between
goroutines. Each send on a particular channel is matched to a
corresponding receive from that channel, usually in a different
goroutine.

A send on a channel happens before the corresponding receive from that
channel completes.

This program:

::

       var c = make(chan int, 10)
       var a string
       
       func f() {
           a = "hello, world"
           c <- 0
       }
       
       func main() {
           go f()
           <-c
           print(a)
       }
       

is guaranteed to print ``"hello, world"``. The write to ``a`` happens
before the send on ``c``, which happens before the corresponding receive
on ``c`` completes, which happens before the ``print``.

The closing of a channel happens before a receive that returns a zero
value because the channel is closed.

In the previous example, replacing ``c <- 0`` with ``close(c)`` yields a
program with the same guaranteed behavior.

A receive from an unbuffered channel happens before the send on that
channel completes.

This program (as above, but with the send and receive statements swapped
and using an unbuffered channel):

::

       var c = make(chan int)
       var a string
       
       func f() {
           a = "hello, world"
           <-c
       }
       
       func main() {
           go f()
           c <- 0
           print(a)
       }
       

is also guaranteed to print ``"hello, world"``. The write to ``a``
happens before the receive on ``c``, which happens before the
corresponding send on ``c`` completes, which happens before the
``print``.

If the channel were buffered (e.g., ``c = make(chan int, 1)``) then the
program would not be guaranteed to print ``"hello, world"``. (It might
print the empty string, crash, or do something else.)

The *k*\ th receive on a channel with capacity *C* happens before the
*k*\ +\ *C*\ th send from that channel completes.

This rule generalizes the previous rule to buffered channels. It allows
a counting semaphore to be modeled by a buffered channel: the number of
items in the channel corresponds to the number of active uses, the
capacity of the channel corresponds to the maximum number of
simultaneous uses, sending an item acquires the semaphore, and receiving
an item releases the semaphore. This is a common idiom for limiting
concurrency.

This program starts a goroutine for every entry in the work list, but
the goroutines coordinate using the ``limit`` channel to ensure that at
most three are running work functions at a time.

::

       var limit = make(chan int, 3)
       
       func main() {
           for _, w := range work {
               go func(w func()) {
                   limit <- 1
                   w()
                   <-limit
               }(w)
           }
           select{}
       }
       

Locks
~~~~~

The ``sync`` package implements two lock data types, ``sync.Mutex`` and
``sync.RWMutex``.

For any ``sync.Mutex`` or ``sync.RWMutex`` variable ``l`` and *n* < *m*,
call *n* of ``l.Unlock()`` happens before call *m* of ``l.Lock()``
returns.

This program:

::

       var l sync.Mutex
       var a string
       
       func f() {
           a = "hello, world"
           l.Unlock()
       }
       
       func main() {
           l.Lock()
           go f()
           l.Lock()
           print(a)
       }
       

is guaranteed to print ``"hello, world"``. The first call to
``l.Unlock()`` (in ``f``) happens before the second call to ``l.Lock()``
(in ``main``) returns, which happens before the ``print``.

For any call to ``l.RLock`` on a ``sync.RWMutex`` variable ``l``, there
is an *n* such that the ``l.RLock`` happens (returns) after call *n* to
``l.Unlock`` and the matching ``l.RUnlock`` happens before call *n*\ +1
to ``l.Lock``.

Once
~~~~

The ``sync`` package provides a safe mechanism for initialization in the
presence of multiple goroutines through the use of the ``Once`` type.
Multiple threads can execute ``once.Do(f)`` for a particular ``f``, but
only one will run ``f()``, and the other calls block until ``f()`` has
returned.

A single call of ``f()`` from ``once.Do(f)`` happens (returns) before
any call of ``once.Do(f)`` returns.

In this program:

::

       var a string
       var once sync.Once
       
       func setup() {
           a = "hello, world"
       }
       
       func doprint() {
           once.Do(setup)
           print(a)
       }
       
       func twoprint() {
           go doprint()
           go doprint()
       }
       

calling ``twoprint`` will call ``setup`` exactly once. The ``setup``
function will complete before either call of ``print``. The result will
be that ``"hello, world"`` will be printed twice.

Incorrect synchronization
-------------------------

Note that a read r may observe the value written by a write w that
happens concurrently with r. Even if this occurs, it does not imply that
reads happening after r will observe writes that happened before w.

In this program:

::

       var a, b int
       
       func f() {
           a = 1
           b = 2
       }
       
       func g() {
           print(b)
           print(a)
       }
       
       func main() {
           go f()
           g()
       }
       

it can happen that ``g`` prints ``2`` and then ``0``.

This fact invalidates a few common idioms.

Double-checked locking is an attempt to avoid the overhead of
synchronization. For example, the ``twoprint`` program might be
incorrectly written as:

::

       var a string
       var done bool
       
       func setup() {
           a = "hello, world"
           done = true
       }
       
       func doprint() {
           if !done {
               once.Do(setup)
           }
           print(a)
       }
       
       func twoprint() {
           go doprint()
           go doprint()
       }
       

but there is no guarantee that, in ``doprint``, observing the write to
``done`` implies observing the write to ``a``. This version can
(incorrectly) print an empty string instead of ``"hello, world"``.

Another incorrect idiom is busy waiting for a value, as in:

::

       var a string
       var done bool
       
       func setup() {
           a = "hello, world"
           done = true
       }
       
       func main() {
           go setup()
           for !done {
           }
           print(a)
       }
       

As before, there is no guarantee that, in ``main``, observing the write
to ``done`` implies observing the write to ``a``, so this program could
print an empty string too. Worse, there is no guarantee that the write
to ``done`` will ever be observed by ``main``, since there are no
synchronization events between the two threads. The loop in ``main`` is
not guaranteed to finish.

There are subtler variants on this theme, such as this program.

::

       type T struct {
           msg string
       }
       
       var g *T
       
       func setup() {
           t := new(T)
           t.msg = "hello, world"
           g = t
       }
       
       func main() {
           go setup()
           for g == nil {
           }
           print(g.msg)
       }
       

Even if ``main`` observes ``g != nil`` and exits its loop, there is no
guarantee that it will observe the initialized value for ``g.msg``.

In all these examples, the solution is the same: use explicit
synchronization.
