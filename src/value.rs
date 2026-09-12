use std::convert::Infallible;
use std::marker::PhantomData;
use std::sync::Arc;

use pyo3::prelude::*;
use pyo3::types::{PyBool, PyString, PyTuple, PyType};
use pyo3::{Borrowed, PyTypeCheck};

pub trait FromRust<T>: Sized {
    fn from_rust(py: Python<'_>, value: &T) -> PyResult<Self>;
}

macro_rules! identity_from_rust {
    ($($ty:ty),+ $(,)?) => {
        $(
            impl FromRust<$ty> for $ty {
                fn from_rust(_py: Python<'_>, value: &$ty) -> PyResult<Self> {
                    Ok(value.clone())
                }
            }
        )+
    };
}

identity_from_rust!(String, bool, char, i32, i64, u32, usize);

impl<T, U: FromRust<T>> FromRust<Option<T>> for Option<U> {
    fn from_rust(py: Python<'_>, value: &Option<T>) -> PyResult<Self> {
        value
            .as_ref()
            .map(|inner| U::from_rust(py, inner))
            .transpose()
    }
}

impl<T, U: FromRust<T>> FromRust<Box<T>> for U {
    fn from_rust(py: Python<'_>, value: &Box<T>) -> PyResult<Self> {
        U::from_rust(py, value)
    }
}

impl<T, U: FromRust<T>> FromRust<Arc<T>> for U {
    fn from_rust(py: Python<'_>, value: &Arc<T>) -> PyResult<Self> {
        U::from_rust(py, value)
    }
}

/// Holds `Py<PyTuple>` so getters hand out the same tuple object every time;
/// `T` only documents and type-checks the element class.
pub struct Seq<T> {
    tuple: Py<PyTuple>,
    element: PhantomData<fn() -> T>,
}

impl<T> Seq<T> {
    pub fn from_items(py: Python<'_>, items: Vec<Py<T>>) -> PyResult<Self> {
        Ok(Self {
            tuple: PyTuple::new(py, items.into_iter().map(Py::into_any))?.unbind(),
            element: PhantomData,
        })
    }
}

impl<T, U> FromRust<Vec<T>> for Seq<U>
where
    Py<U>: FromRust<T>,
{
    fn from_rust(py: Python<'_>, value: &Vec<T>) -> PyResult<Self> {
        let items = value
            .iter()
            .map(|item| Py::<U>::from_rust(py, item))
            .collect::<PyResult<Vec<_>>>()?;
        Self::from_items(py, items)
    }
}

impl<'a, 'py, T: PyTypeCheck + 'static> FromPyObject<'a, 'py> for Seq<T> {
    type Error = PyErr;

    fn extract(obj: Borrowed<'a, 'py, PyAny>) -> PyResult<Self> {
        let items: Vec<Py<T>> = obj.extract()?;
        Self::from_items(obj.py(), items)
    }
}

impl<'py, T> IntoPyObject<'py> for Seq<T> {
    type Target = PyTuple;
    type Output = Bound<'py, PyTuple>;
    type Error = Infallible;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Ok(self.tuple.into_bound(py))
    }
}

impl<'a, 'py, T: 'a> IntoPyObject<'py> for &'a Seq<T> {
    type Target = PyTuple;
    type Output = Borrowed<'a, 'py, PyTuple>;
    type Error = Infallible;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Ok(self.tuple.bind_borrowed(py))
    }
}

fn match_args<'py>(cls: &Bound<'py, PyType>) -> PyResult<Bound<'py, PyTuple>> {
    Ok(cls.getattr("__match_args__")?.cast_into::<PyTuple>()?)
}

/// Equal when the class matches and every `__match_args__` field is equal;
/// `NotImplemented` for any other class, so Python tries the reflected
/// comparison.
pub fn structural_eq<'py>(
    slf: &Bound<'py, PyAny>,
    other: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let py = slf.py();
    let cls = slf.get_type();
    if !other.get_type().is(&cls) {
        return Ok(py.NotImplemented().into_bound(py));
    }
    for name in match_args(&cls)?.iter() {
        let name = name.cast_into::<PyString>()?;
        if !slf.getattr(&name)?.eq(other.getattr(&name)?)? {
            return Ok(PyBool::new(py, false).to_owned().into_any());
        }
    }
    Ok(PyBool::new(py, true).to_owned().into_any())
}

pub type NodeReduction<'py> = (Bound<'py, PyType>, Bound<'py, PyTuple>);

pub type MemberReduction<'py> = (Bound<'py, PyAny>, (Bound<'py, PyType>, &'static str));

/// `(cls, args)` over `__match_args__`, so `pickle` and `copy` rebuild the
/// node through its positional constructor.
pub fn structural_reduce<'py>(slf: &Bound<'py, PyAny>) -> PyResult<NodeReduction<'py>> {
    let cls = slf.get_type();
    let args = match_args(&cls)?
        .iter()
        .map(|name| slf.getattr(name.cast_into::<PyString>()?))
        .collect::<PyResult<Vec<_>>>()?;
    Ok((cls, PyTuple::new(slf.py(), args)?))
}

/// `Qualname(field=repr, ...)` over the class's `__match_args__`.
pub fn structural_repr(slf: &Bound<'_, PyAny>) -> PyResult<String> {
    let cls = slf.get_type();
    let mut fields = Vec::new();
    for name in match_args(&cls)?.iter() {
        let name = name.cast_into::<PyString>()?;
        let value = slf.getattr(&name)?.repr()?;
        fields.push(format!("{name}={value}"));
    }
    Ok(format!("{}({})", cls.qualname()?, fields.join(", ")))
}

/// Defines a frozen struct node with a positional constructor, getters for
/// every field, `__match_args__`, structural equality, `__hash__ = None` and
/// `__reduce__`.
macro_rules! node_struct {
    (
        $(#[$meta:meta])*
        $name:ident { $( $(#[$field_meta:meta])* $field:ident : $ty:ty ),+ $(,)? }
    ) => {
        $(#[$meta])*
        #[::pyo3::pyclass(frozen, get_all, module = "brush_parser._core")]
        pub struct $name {
            $( $(#[$field_meta])* pub(crate) $field: $ty, )+
        }

        #[::pyo3::pymethods]
        impl $name {
            #[new]
            fn new($($field: $ty),+) -> Self {
                Self { $($field),+ }
            }

            #[classattr]
            fn __match_args__(
                py: ::pyo3::Python<'_>,
            ) -> ::pyo3::PyResult<::pyo3::Bound<'_, ::pyo3::types::PyTuple>> {
                ::pyo3::types::PyTuple::new(py, [$(stringify!($field)),+])
            }

            #[classattr]
            const __hash__: Option<::pyo3::Py<::pyo3::PyAny>> = None;

            fn __eq__<'py>(
                slf: &::pyo3::Bound<'py, Self>,
                other: &::pyo3::Bound<'py, ::pyo3::PyAny>,
            ) -> ::pyo3::PyResult<::pyo3::Bound<'py, ::pyo3::PyAny>> {
                $crate::value::structural_eq(slf.as_any(), other)
            }

            fn __repr__(slf: &::pyo3::Bound<'_, Self>) -> ::pyo3::PyResult<String> {
                $crate::value::structural_repr(slf.as_any())
            }

            fn __reduce__<'py>(
                slf: &::pyo3::Bound<'py, Self>,
            ) -> ::pyo3::PyResult<$crate::value::NodeReduction<'py>> {
                $crate::value::structural_reduce(slf.as_any())
            }
        }
    };
}

/// Defines a complex enum node: one frozen subclass per variant with the
/// constructor and `__match_args__` pyo3 generates, plus structural equality,
/// `__hash__ = None` and `__reduce__` inherited from the base class.
macro_rules! node_enum {
    (
        $(#[$meta:meta])*
        $name:ident {
            $(
                $(#[$variant_meta:meta])*
                $variant:ident { $( $(#[$field_meta:meta])* $field:ident : $ty:ty ),* $(,)? }
            ),+ $(,)?
        }
    ) => {
        $(#[$meta])*
        #[::pyo3::pyclass(module = "brush_parser._core")]
        pub enum $name {
            $( $(#[$variant_meta])* $variant { $( $(#[$field_meta])* $field: $ty ),* }, )+
        }

        #[::pyo3::pymethods]
        impl $name {
            #[classattr]
            const __hash__: Option<::pyo3::Py<::pyo3::PyAny>> = None;

            fn __eq__<'py>(
                slf: &::pyo3::Bound<'py, Self>,
                other: &::pyo3::Bound<'py, ::pyo3::PyAny>,
            ) -> ::pyo3::PyResult<::pyo3::Bound<'py, ::pyo3::PyAny>> {
                $crate::value::structural_eq(slf.as_any(), other)
            }

            fn __repr__(slf: &::pyo3::Bound<'_, Self>) -> ::pyo3::PyResult<String> {
                $crate::value::structural_repr(slf.as_any())
            }

            fn __reduce__<'py>(
                slf: &::pyo3::Bound<'py, Self>,
            ) -> ::pyo3::PyResult<$crate::value::NodeReduction<'py>> {
                $crate::value::structural_reduce(slf.as_any())
            }
        }
    };
}

/// Defines a unit-only enum as a pyo3 simple enum with `PartialEq` equality,
/// `__hash__ = None` and `__reduce__` through `getattr(cls, name)`.
macro_rules! unit_enum {
    (
        $(#[$meta:meta])*
        $name:ident { $( $(#[$variant_meta:meta])* $variant:ident ),+ $(,)? }
    ) => {
        $(#[$meta])*
        #[::pyo3::pyclass(frozen, eq, skip_from_py_object, module = "brush_parser._core")]
        #[derive(Clone, Copy, PartialEq, Eq)]
        pub enum $name {
            $( $(#[$variant_meta])* $variant, )+
        }

        #[::pyo3::pymethods]
        impl $name {
            #[classattr]
            const __hash__: Option<::pyo3::Py<::pyo3::PyAny>> = None;

            fn __reduce__<'py>(
                slf: &::pyo3::Bound<'py, Self>,
            ) -> ::pyo3::PyResult<$crate::value::MemberReduction<'py>> {
                let member = match *slf.get() {
                    $( Self::$variant => stringify!($variant), )+
                };
                $crate::value::member_reduce(slf.as_any(), member)
            }
        }
    };
}

/// `(getattr, (cls, member))`, so `pickle` and `copy` resolve a unit-enum
/// member back to the class attribute.
pub fn member_reduce<'py>(
    slf: &Bound<'py, PyAny>,
    member: &'static str,
) -> PyResult<MemberReduction<'py>> {
    let getattr = slf.py().import("builtins")?.getattr("getattr")?;
    Ok((getattr, (slf.get_type(), member)))
}

/// Implements [`FromRust`] for a struct node by converting each listed
/// source expression into the matching field.
macro_rules! from_rust_struct {
    (
        $rust:ty => $node:ident, $value:ident { $( $field:ident : $source:expr ),+ $(,)? }
    ) => {
        impl $crate::value::FromRust<$rust> for ::pyo3::Py<$node> {
            fn from_rust(py: ::pyo3::Python<'_>, $value: &$rust) -> ::pyo3::PyResult<Self> {
                ::pyo3::Py::new(
                    py,
                    $node { $( $field: $crate::value::FromRust::from_rust(py, &$source)? ),+ },
                )
            }
        }
    };
}

/// Implements [`FromRust`] for a unit enum by mapping variants by name.
macro_rules! from_rust_unit_enum {
    ($module:ident :: $rust:ident => $node:ident { $($variant:ident),+ $(,)? }) => {
        impl $crate::value::FromRust<$module::$rust> for ::pyo3::Py<$node> {
            fn from_rust(
                py: ::pyo3::Python<'_>,
                value: &$module::$rust,
            ) -> ::pyo3::PyResult<Self> {
                let node = match value {
                    $( $module::$rust::$variant => $node::$variant, )+
                };
                ::pyo3::Py::new(py, node)
            }
        }
    };
}

/// A complex-enum value lands on its variant subclass only through
/// `IntoPyObject`, not through `Py::new`.
pub fn enum_node<'py, E>(py: Python<'py>, node: E) -> PyResult<Py<E>>
where
    E: IntoPyObject<'py, Target = E, Output = Bound<'py, E>, Error = PyErr>,
{
    Ok(node.into_pyobject(py)?.unbind())
}

pub(crate) use {from_rust_struct, from_rust_unit_enum, node_enum, node_struct, unit_enum};
